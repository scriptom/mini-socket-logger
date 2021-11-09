import socket
from datetime import datetime
from typing import Optional

from helper import get_protocol_from_cli_arguments, AUTH_TOKEN


class AuthHandler(object):
    _users = []

    def __init__(self, users_file):
        with open(users_file, 'r') as f:
            self._users = f.read().splitlines()

    def user_exists(self, user: str) -> bool:
        return user in self._users

    @classmethod
    def parse_username_from_message(cls, message: str) -> Optional[str]:
        if message.startswith(AUTH_TOKEN):
            return message.split(' ')[1]
        return None


class SimpleLogger:
    _log_file: str

    def __init__(self, log_file: str) -> None:
        self._log_file = log_file

    def write(self, message: str) -> None:
        now = datetime.now()
        with open(self._log_file, 'a', encoding='utf8') as f:
            f.write(f'{now} - {message}')


class SocketWrapper(object):
    _socket: socket.socket = None
    _protocol: str = None
    _buffer_size: int = 1024
    _logger: SimpleLogger = SimpleLogger('log.txt')
    _auth_handler: AuthHandler = AuthHandler('users.txt')
    EXIT_MESSAGE = b'EXIT'
    KEEPALIVE_MESSAGE = b'KEEPALIVE'
    AUTH_COMPLETED_MESSAGE = b'OK'
    AUTH_FAILED_MESSAGE = b'INVALIDUSER'

    def __init__(self, s: socket.socket, protocol: str):
        super().__init__()
        self._polling = True
        self._socket = s
        self._protocol = protocol

    def poll_messages(self) -> None:
        message, address = self._poll(self._buffer_size)
        self.log_message(message.decode('utf-8'), address)
        if username := AuthHandler.parse_username_from_message(message.decode('utf-8')):
            if self._auth_handler.user_exists(username):
                self._respond_with(self.AUTH_COMPLETED_MESSAGE, address)
            else:
                self._respond_with(self.AUTH_FAILED_MESSAGE, address)
            return

        if message == self.EXIT_MESSAGE:
            # We let the client know that we are closing the connection
            self._respond_with(self.EXIT_MESSAGE, address)
            self.dispose()
            print(f'{self._protocol} - Connection closed')
        else:
            # We let the client know that we are still alive
            self._respond_with(self.KEEPALIVE_MESSAGE, address)

    def log_message(self, message: str, address) -> None:
        self._logger.write(f' {address} [{self._protocol}]: {message}\n')

    def dispose(self) -> None:
        self._polling = False
        self._socket.close()

    def _poll(self, buffer_size: int) -> (bytes, tuple):
        raise NotImplementedError()

    def _respond_with(self, message: bytes, address: tuple = None) -> None:
        raise NotImplementedError()

    @property
    def polling(self) -> bool:
        return self._polling

    @classmethod
    def create_udp_socket(cls, host: str, port: int) -> 'SocketWrapper':
        # Create a UDP socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind the socket to the port
        udp_socket.bind((host, port))
        print(f'UDP - Listening on {host}:{port}')
        return UDPSocket(udp_socket)

    @classmethod
    def create_tcp_socket(cls, host: str, port: int) -> 'SocketWrapper':
        # Create a TCP socket
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the port
        tcp_socket.bind((host, port))
        # Listen for incoming connections
        tcp_socket.listen(1)
        print(f'TCP - Listening on {host}:{port}')
        return TCPSocket(tcp_socket)


class UDPSocket(SocketWrapper):
    def _respond_with(self, message: bytes, address: tuple = None) -> None:
        self._socket.sendto(message, address)

    def __init__(self, _socket):
        super(UDPSocket, self).__init__(_socket, 'UDP')

    def _poll(self, buffer_size: int) -> (bytes, tuple):
        return self._socket.recvfrom(buffer_size)


class TCPSocket(SocketWrapper):
    def _respond_with(self, message: bytes, address: tuple = None) -> None:
        self._conn.sendto(message, self._address)

    def __init__(self, _socket):
        super().__init__(_socket, 'TCP')
        conn, address = self._socket.accept()
        self._conn = conn
        self._address = address

    def _poll(self, buffer_size: int) -> (bytes, tuple):
        return self._conn.recv(buffer_size), self._address


class SocketFactory:
    @classmethod
    def socket_for_protocol(cls, host: str, port: int, protocol: str) -> Optional[SocketWrapper]:
        p = protocol.lower()
        if p == 'udp':
            return SocketWrapper.create_udp_socket(host, port)

        if p == 'tcp':
            return SocketWrapper.create_tcp_socket(host, port)
        return None


def main():
    host = 'localhost'
    port = 19876
    protocol = get_protocol_from_cli_arguments()
    sock = SocketFactory.socket_for_protocol(host, port, protocol)
    if sock is not None:
        while sock.polling:
            sock.poll_messages()


if __name__ == '__main__':
    main()
