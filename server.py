import socket
from threading import Thread
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a well-known port
serversocket.bind(('localhost', 80))
# become a server socket
serversocket.listen(5)


def recvall(sock):
    print('connected')
    bs = 4096
    data = bytearray()
    while True:
        part = sock.recv(bs)
        data.extend(part)
        if len(part) < bs:
            break
    print(len(data))
    return data

def write_file(sock):
    data = recvall(sock)
    out = open('test_recieved/output.zip', "wb")
    out.write(data)
    out.close()
while True:
    # accept connections from outside
    (clientsocket, address) = serversocket.accept()
    if address:
        Thread(write_file(clientsocket)).run()

    # now do something with the clientsocket


