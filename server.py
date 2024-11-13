import socket, os
from threading import Thread
import sqlite3
import uuid
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a well-known port
serversocket.bind(('localhost', 80))
# become a server socket
serversocket.listen(5)

con = sqlite3.connect("files.sqlite")
cur = con.cursor()

def recvall(sock, address):
    BUFFER_SIZE = 4096
    SEPARATOR = "<"
    received = client_socket.recv(BUFFER_SIZE).decode()
    elem1, elem2 = received.split(SEPARATOR)
    if elem1 == "%SEARCH%":
        send_info(elem2.replace(" ", ""), sock)
    elif elem1 == "%download%":
        send_f(client_socket, elem2.replace(" ", ""))
    else:
        work_dir = os.getcwd()
        if not os.path.exists(f"{work_dir}/{address[0]}"):
            os.makedirs(f"{work_dir}/{address[0]}")

        elem1 = os.path.basename(elem1)
        elem1 = f'{work_dir}/{address[0]}/{elem1}'
        print(elem1)
        with open(elem1, "wb") as f:
            while True:
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:
                    break
                f.write(bytes_read)
        return_passcode(sock, address[0], elem1[elem1.rfind("/") + 1:])
    sock.close()


def return_passcode(sock: socket.socket, folder, name):
    while True:
        uid = str(uuid.uuid4())[:8]
        result = cur.execute(f"select path from path_n_uid where uid = '{uid}'").fetchone()
        if not result:
            cur.execute(f"INSERT INTO path_n_uid (uid, path) VALUES ('{uid}', '{name}')")
            con.commit()
            break
    sock.sendall(uid.encode())


def send_info(passcode, sock: socket.socket):
    result = cur.execute(f"select path from path_n_uid where uid = '{passcode}'").fetchone()
    print(result)
    if not result:
        sock.sendall(str.encode((" " * 4096)))
    else:
        file = str(result[0])
        filename = file[file.rfind("/") + 1:] + "<"
        size = os.path.getsize(file[file.rfind("/") + 1:])
        print(size)
        sock.sendall(str.encode(filename + str(size) + (" " * (4096 - len(str.encode(filename + str(size)))))))

def send_f(connection: socket.socket, passcode):
    BUFFER_SIZE = 4096
    print([i for i in passcode])
    result = cur.execute(f"select path from path_n_uid where uid = '{passcode}'").fetchone()
    print(result[0])
    with open(result[0], "rb") as f:
        print(result[0])
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            connection.sendall(bytes_read)
            print(2)

while True:
    # accept connections from outside
    (client_socket, address) = serversocket.accept()
    if address:
        Thread(recvall(client_socket, address)).run()

    # now do something with the clientsocket


