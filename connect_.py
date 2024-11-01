import socket


class connect_:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, server, sockt):
        self.sock.connect((server, int(sockt)))

    def sendfile(self, byts):
        self.sock.sendall(byts)

