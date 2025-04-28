import os
import socket
import sqlite3
import sys
import threading
import uuid
from threading import Thread
import time
import colorama
import tqdm


def write_props(port):
    f = open("../server_props.txt", "w")
    f.write("port: " + port)

def create_database():
    file = open("files.sqlite", "w")
    file.close()
    con = sqlite3.connect((os.getcwd() + "/files.sqlite"))
    cur = con.cursor()
    cur.execute("CREATE TABLE path_n_uid (uid  TEXT, path TEXT);")
    con.commit()

def read_props():
    try:
        line = open("../server_props.txt").readline()
        return line[line.find(" ") + 1:].rstrip('\n')
    except FileNotFoundError:
        write_props("80")
        return read_props()


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def con_reload():
    serversocket.bind(('0.0.0.0', int(read_props())))
    serversocket.listen(20)


con_reload()
print("чтобы сменить порт напишите: port [ваш порт]")


def thr_inp():
    while True:
        try:
            inp = input()
            if inp[:inp.find(" ")] == "port":
                write_props(inp[inp.find(" ") + 1:])
                global serversocket
                serversocket.close()
                serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                con_reload()
                print("Порт успешно сменён на", inp[inp.find(" ") + 1:])
        except UnicodeDecodeError:
            pass


def main_recieve():
    while True:
        try:
            (client_socket, address) = serversocket.accept()
            if address:
                Thread(recvall(client_socket, address)).run()
        except OSError:
            pass


def recvall(sock, address):
    BUFFER_SIZE = 4096
    SEPARATOR = "<"
    received = sock.recv(BUFFER_SIZE).decode()
    if received != '':

        try:
            elem1, elem2 = received.split(SEPARATOR)
            if elem1 == "%SEARCH%":
                send_info(elem2.replace(" ", ""), sock)
            elif elem1 == "%download%":
                send_f(sock, elem2.replace(" ", ""))
            else:
                f_b = read_bar_format = "{l_bar}{bar}"

                elem1 = os.path.basename(elem1)
                info_pb = F"{elem1} от {str(address[0]) }:{ str(address[1])}"
                progress = tqdm.tqdm(range(100), desc=(colorama.Style.DIM + ("Получение файла " + info_pb)),
                                        bar_format=f_b,
                                        colour="white")
                work_dir = os.getcwd()
                now = 0
                step = (100 / int(elem2)) * BUFFER_SIZE
                if not os.path.exists(f"{work_dir}/{address[0]}"):
                    os.makedirs(f"{work_dir}/{address[0]}")

                elem1 = f'{work_dir}/{address[0]}/{elem1}'
                sock.sendall("ok".encode())
                with open(elem1, "wb") as f:
                    while True:
                        bytes_read = sock.recv(BUFFER_SIZE)
                        if len(bytes_read) == 0:
                            break
                        f.write(bytes_read)
                        now += step
                        if (now > 1):
                            progress.update(round(now, 0))
                            now -= round(now, 0)
                        sock.sendall("ok".encode())
                progress.update(100)
                progress.set_description_str((colorama.Style.DIM + ("Получен файл " + info_pb)))
                print(121212)
                return_passcode(sock, address[0], elem1)
            sock.close()
        except ConnectionResetError as e:
            print(f"Пользователь {str(address[0]) }:{ str(address[1])} разорвал подключение")
        except ValueError:
            pass








def return_passcode(sock: socket.socket, folder, name):
    try:
        open("files.sqlite", "r")
    except FileNotFoundError:
        create_database()
    con = sqlite3.connect((os.getcwd() + "/files.sqlite"))
    cur = con.cursor()
    while True:
        uid = str(uuid.uuid4())[:8]
        result = cur.execute(f"select path from path_n_uid where uid = '{uid}'").fetchone()
        if not result:
            cur.execute(f"INSERT INTO path_n_uid (uid, path) VALUES ('{uid}', '{name}')")
            con.commit()
            break
    cur.close()
    sock.sendall(uid.encode())


def send_info(passcode, sock: socket.socket):
    try:
        open("files.sqlite", "r")
    except FileNotFoundError:
        create_database()
    con = sqlite3.connect((os.getcwd() + "/files.sqlite"))
    cur = con.cursor()
    result = cur.execute(f"select path from path_n_uid where uid = '{passcode}'").fetchone()
    if not result:
        sock.sendall(str.encode((" " * 4096)))
    else:
        file = str(result[0])
        filename = file[file.rfind('/') + 1:] + "<"
        size = os.path.getsize(file)
        sock.sendall(str.encode(filename + str(size) + (" " * (4096 - len(str.encode(filename + str(size)))))))
        print(f"Информация о файле {file[file.rfind('/') + 1:]} отправлена на {sock.getpeername()[0]}:{sock.getpeername()[1]}")


def send_f(connection: socket.socket, passcode):
    try:
        open("files.sqlite", "r")
    except FileNotFoundError:
        create_database()
    con = sqlite3.connect((os.getcwd() + "/files.sqlite"))
    cur = con.cursor()
    BUFFER_SIZE = 4096
    result = cur.execute(f"select path from path_n_uid where uid = '{passcode}'").fetchone()
    info_pb = F"файла {result[0][result[0].rfind('/') + 1:]} на {connection.getpeername()[0]}:{connection.getpeername()[1]}"
    f_b = read_bar_format = "{l_bar}{bar}"
    progress = tqdm.tqdm(range(100), desc=(colorama.Style.DIM + ("Отправка " + info_pb)), bar_format=f_b,
                         colour="white")
    step = (100 / int(os.path.getsize(result[0]))) * BUFFER_SIZE
    now = 0
    with open(result[0], "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            connection.sendall(bytes_read)
            now += 1
            if (now > 1):
                progress.update(round(now, 0))
                now -= round(now, 0)
    progress.update(100)
    progress.set_description_str((colorama.Style.DIM + F"Файл {result[0][result[0].rfind('/') + 1:]} отправлен на {connection.getpeername()[0]}:{connection.getpeername()[1]}"))

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
sys.excepthook = except_hook
t1 = threading.Thread(target=main_recieve)
t2 = threading.Thread(target=thr_inp)

t1.start()
t2.start()
t1.join()
t2.join()
