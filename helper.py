import getopt
import sys


def get_protocol_from_cli_arguments() -> str:
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:", ["protocol="])
        for opt, arg in opts:
            if opt in ("-p", "--protocol") and arg in ("tcp", "udp", "UDP", "TCP"):
                return arg
    except getopt.GetoptError:
        print("Invalid argument")
        sys.exit(2)

AUTH_TOKEN = 'helloiam'
