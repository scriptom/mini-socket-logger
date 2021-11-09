import socket
import sys

from helper import get_protocol_from_cli_arguments, AUTH_TOKEN


def main():
    host = 'localhost'
    port = 19876
    buffer_size = 1024
    protocol = get_protocol_from_cli_arguments()
    if protocol == "tcp":
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    elif protocol == "udp":
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        print("Invalid protocol")
        sys.exit(2)

    s.connect((host, port))
    username = input("Username: ")
    s.send(f'{AUTH_TOKEN} {username}'.encode('utf-8'))
    res = s.recv(buffer_size).decode('utf-8')
    if res == 'OK':
        while True:
            # Get input from user
            data = input("server.py> ")
            # Send data to server
            s.send(data.encode())
            # Receive data from server
            data = s.recv(buffer_size)
            if data.decode('utf-8').lower() == "exit":
                break
    else:
        print('Invalid user')

    print("Closing connection")
    s.close()


if __name__ == '__main__':
    main()
