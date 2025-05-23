import threading
import time

import PyQt6.QtCore
import PyQt6.QtGui
import PyQt6.QtWidgets
import datetime
import os
import pathlib
import progress_client
import socket
import start_client
import sys

import PyQt6
from PyQt6.QtCore import Qt

import search_ui


def read_props():
    try:
        f = open("properties.txt", "r")
        mas = []
        for i in f.readlines():
            mas.append(i[i.find(" ") + 1:].rstrip('\n'))
        f.close()
        return mas
    except FileNotFoundError:
        f = open("properties.txt", "w")
        f.write(f"ip: {socket.gethostbyname(socket.gethostname())}\nport: 80")
        return ["localhost", 80]


def read_history():
    try:
        f = open("history.txt", "r")
        mas = []
        for i in f.readlines():
            mas.append(i.rstrip('\n'))
        f.close()
        return mas
    except FileNotFoundError:
        f = open("history.txt", "w")
        f.close()


class settings_window(PyQt6.QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Настройки")
        self.setFixedSize(300, 250)
        self.setlbl = PyQt6.QtWidgets.QLabel(self)
        self.setlbl.setText('Настройки')
        self.setlbl.move(0, 0)
        self.lbl1 = PyQt6.QtWidgets.QLabel(self)
        self.lbl1.setText('Ip')
        self.lbl1.move(120, 20)
        self.ip = PyQt6.QtWidgets.QLineEdit(self)
        self.ip.move(100, 60)
        props = read_props()
        self.ip.setText(props[0])
        self.lbl2 = PyQt6.QtWidgets.QLabel(self)
        self.lbl2.setText('Порт')
        self.lbl2.move(120, 100)
        self.port = PyQt6.QtWidgets.QLineEdit(self)
        self.port.move(100, 140)
        self.port.setText(str(props[1]))
        self.confirm = PyQt6.QtWidgets.QPushButton(self)
        self.confirm.move(100, 190)
        self.confirm.setText("Готово")
        self.confirm.clicked.connect(self.conf)

    def conf(self):

        if self.port.text() and self.ip.text():
            f = open("properties.txt", "w")
            ip = 'ip: ' + self.ip.text() + '\n'
            port = 'port: ' + self.port.text() + '\n'
            mas = [ip, port]
            f.write("".join(mas))
            f.close()
            self.close()
        else:
            self.statusBar().setStyleSheet("color: red;")
            self.statusBar().showMessage("Поля не должны быть пустыми", 3000)


class start_window(PyQt6.QtWidgets.QMainWindow, start_client.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.settings = PyQt6.QtWidgets.QPushButton(self)
        self.setWindowTitle("Фалообменник")
        self.settings.setIcon(PyQt6.QtGui.QIcon('settings.png'))
        self.settings.resize(40, 40)
        self.settings.move(420, 0)
        self.history = PyQt6.QtWidgets.QPushButton(self)
        self.history.setIcon(PyQt6.QtGui.QIcon('history.png'))
        self.history.resize(40, 40)
        self.history.move(370, 0)
        self.settings.clicked.connect(self.open_settings)
        self.pushButton.clicked.connect(self.upload)
        self.pushButton_2.clicked.connect(self.get)
        self.history.clicked.connect(self.open_history)

    def open_settings(self):
        self.wind = settings_window()
        self.wind.show()

    def open_history(self):
        self.hwind = history()
        self.hwind.show()

    def upload(self):
        try:
            self.uploadwind = load_file()
        except ConnectionRefusedError:
            self.statusBar().setStyleSheet("color: red")
            self.statusBar().showMessage("Такого сервера не существует или он отключён", 2500)
        except ConnectionResetError:
            self.statusBar().setStyleSheet("color: red")
            self.statusBar().showMessage("Сервер разорвал подключение", 2500)

    def get(self):
        try:
            self.getfilewind = get_file()
            self.getfilewind.show()
        except ConnectionRefusedError:
            self.statusBar().setStyleSheet("color: red")
            self.statusBar().showMessage("Такого сервера не существует или он отключён", 2500)
        except ConnectionResetError:
            self.statusBar().setStyleSheet("color: red")
            self.statusBar().showMessage("Сервер разорвал подключение", 2500)


class history(PyQt6.QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("История")
        self.setFixedSize(500, 500)
        self.label = PyQt6.QtWidgets.QLabel(self)
        self.label.setText("История")
        self.label.move(25, 20)
        font = PyQt6.QtGui.QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setFixedSize(self.label.size().width() + 15, self.label.size().height())
        self.delt = PyQt6.QtWidgets.QPushButton("Очистить", self)
        self.delt.move(350, 20)
        self.qlist = PyQt6.QtWidgets.QListWidget(self)
        self.qlist.move(25, 100)
        self.qlist.setFixedSize(450, 380)
        self.read_h()
        self.delt.clicked.connect(self.delete)

    def read_h(self):
        try:
            for i in read_history():
                self.qlist.addItem(i)
        except TypeError:
            pass

    def delete(self):
        self.qlist.clear()
        open('history.txt', "w").write('')


class load_file(PyQt6.QtWidgets.QMainWindow, progress_client.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        super().setupUi(self)

        self.setWindowTitle("Загрузка файла")
        self.setFixedSize(self.size())
        self.Done_button.hide()
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.Done_button.clicked.connect(self.close)
        self.pass_lbl = PyQt6.QtWidgets.QLabel(self)
        self.pass_lbl.move(120, 55)
        self.pass_lbl.hide()
        self.send_f()

    def send_f(self):
        SEPARATOR = "<"
        BUFFER_SIZE = 4096
        self.file = PyQt6.QtWidgets.QFileDialog.getOpenFileName(self)[0]
        if os.path.basename(self.file) == "":
            return
        self.show()
        PyQt6.QtWidgets.QApplication.processEvents()
        filesize = os.path.getsize(self.file)
        ip = read_props()[0]
        port = read_props()[1]
        step = 100 / (filesize / BUFFER_SIZE)
        now = 0
        connection = socket.socket()
        connection.connect((ip, int(port)))
        info = str(self.file) + SEPARATOR + str(filesize)
        PyQt6.QtWidgets.QApplication.processEvents()
        if len(str.encode(info)) < 4096:
            info += (" " * (4096 - len(str.encode(info))))
            connection.sendall(str.encode(info))
        else:
            connection.send(f"{self.file}{SEPARATOR}{filesize}".encode())
        with open(self.file, "rb") as f:
            while True:
                PyQt6.QtWidgets.QApplication.processEvents()
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                connection.sendall(bytes_read)
                now += step
                if now > 1:
                    self.progressBar.setValue(self.progressBar.value() + int(now))
                    now -= int(now)
        self.progressBar.setValue(100)
        passcode = connection.recv(8).decode()
        self.Status_lbl.setText("Файл загружен")
        self.pass_lbl.setFixedSize(200, 30)
        self.pass_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.pass_lbl.setText(f"Код файла: {passcode}")
        self.pass_lbl.show()
        size_form = filesize / (1024 ** 2)
        open("history.txt", "a").write((self.file[self.file.rfind('/') + 1:] + " " + str(
            round(size_form, 1)) + " Mb " + str(datetime.datetime.now())[:10] + " " + passcode + ' \n'))
        self.Done_button.show()
        connection.close()

    def closeEvent(self, a0):
        pass


class get_file(PyQt6.QtWidgets.QMainWindow, search_ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        super().setupUi(self)
        self.download_btn.hide()
        self.progressBar = PyQt6.QtWidgets.QProgressBar(self)
        self.progressBar.setRange(0, 100)
        self.progressBar.setGeometry(PyQt6.QtCore.QRect(20, 200, 481, 31))
        self.progressBar.setValue(0)
        self.progressBar.hide()
        self.setWindowTitle("Получение файла")
        self.size_of_file = PyQt6.QtWidgets.QLabel(self)
        self.size_of_file.move(20, 150)
        self.search_btn.clicked.connect(self.search)
        self.download_btn.setText("")
        self.download_btn.setIcon(PyQt6.QtGui.QIcon("download.png"))
        self.download_btn.clicked.connect(self.download)

    def search(self):
        self.progressBar.hide()
        SEPARATOR = "<"
        BUFFER_SIZE = 4096
        ip = read_props()[0]
        port = read_props()[1]
        self.connection = socket.socket()
        self.connection.connect((ip, int(port)))
        info = "%SEARCH%<" + self.search_line.text().replace(" ", "")
        self.passcode = self.search_line.text().replace(" ", "")
        if len(str.encode(info)) < 4087:
            info += (" " * (4087 - len(str.encode(info))))
            self.connection.sendall(str.encode(info))
        else:
            self.connection.sendall(str.encode(info))
        try:
            self.filename, self.filesize = self.connection.recv(4096).decode().split(SEPARATOR)
            self.file_name.setText(self.filename)
            self.size_of_file.setText(str(round(eval(self.filesize + "/1048576"), 1)) + "Mb")
            self.download_btn.show()
        except ValueError:
            self.file_name.setText("Файл не найден")
            self.download_btn.hide()
            self.size_of_file.setText("")

    def download(self):
        dir_path = PyQt6.QtWidgets.QFileDialog.getExistingDirectory(self)
        if dir_path == "":
            return
        self.progressBar.show()
        self.progressBar.setValue(0)
        PyQt6.QtWidgets.QApplication.processEvents()
        info = "%download%<" + self.passcode
        ip = read_props()[0]
        port = read_props()[1]
        step = 100 / (int(self.filesize) / 4096)
        now = 0
        connection = socket.socket()
        connection.connect((ip, int(port)))
        if len(str.encode(info)) < 4096:
            info += (" " * (4096 - len(str.encode(info))))
            connection.sendall(str.encode(info))
        else:
            connection.send(info.encode())
        BUFFER_SIZE = 4096
        with open(f"{dir_path}/{self.filename}", "wb") as f:
            while True:
                bytes_read = connection.recv(BUFFER_SIZE)
                if not bytes_read:
                    break
                f.write(bytes_read)
                now += step
                if now > 1:
                    self.progressBar.setValue(self.progressBar.value() + int(now))
                    now -= int(now)
        self.progressBar.setValue(100)
        threading.Thread(target=self.progress_bar_close).start()

    def progress_bar_close(self):
        time.sleep(2)
        self.progressBar.hide()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = PyQt6.QtWidgets.QApplication(sys.argv)
    path = os.getcwd() + "/fonts/jetbrains.ttf"
    PyQt6.QtGui.QFontDatabase.addApplicationFont(path)
    ex = start_window()
    app.setFont(PyQt6.QtGui.QFont('JetBrains Mono NL'))
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
