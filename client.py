import socket, start_client, PyQt6.QtWidgets, sys, PyQt6.QtGui, progress_client, PyQt6.QtCore
import pathlib, os
import threading
import search_ui
import PyQt6, time
from PyQt6.QtCore import Qt

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
        f.write("ip: localhost\nport: 80")
        return ["localhost", 80]


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
        self.port.setText(props[1])
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
        self.settings.clicked.connect(self.open_settings)
        self.pushButton.clicked.connect(self.upload)
        self.pushButton_2.clicked.connect(self.get)

    def open_settings(self):
        self.wind = settings_window()
        self.wind.show()

    def upload(self):
        self.uploadwind = load_file()
        self.uploadwind.show()

    def get(self):
        self.getfilewind = get_file()
        self.getfilewind.show()



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
        threading.Thread(self.send_f()).run()

    def send_f(self):
        SEPARATOR = "<"
        BUFFER_SIZE = 4096
        self.file = PyQt6.QtWidgets.QFileDialog.getOpenFileName(self)[0]
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

        passcode = connection.recv(8).decode()
        self.Status_lbl.setText("Файл загружен")
        self.pass_lbl.setFixedSize(200, 30)
        self.pass_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.pass_lbl.setText(f"Код файла: {passcode}")
        self.pass_lbl.show()
        self.Done_button.show()
        connection.close()

class get_file(PyQt6.QtWidgets.QMainWindow,search_ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        super().setupUi(self)
        self.download_btn.hide()
        self.search_btn.clicked.connect(self.search)
        self.download_btn.setIcon(PyQt6.QtGui.QIcon("download.png"))
        self.download_btn.clicked.connect(self.download)

    def search(self):
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
        self.filename = self.connection.recv(4096).decode()
        self.file_name.setText(self.filename)
        self.download_btn.show()

    def download(self):
        HOME_PATH = os.getenv("HOME")
        dir_path = PyQt6.QtWidgets.QFileDialog.getExistingDirectory(
            parent=self,
            caption="Select directory",
            directory=HOME_PATH,
            options=PyQt6.QtWidgets.QFileDialog.Option.DontUseNativeDialog,
        )
        print(f"{dir_path}/{self.filename}")
        info = "%download%<" + self.passcode
        if len(str.encode(info)) < 4096:
            info += (" " * (4096 - len(str.encode(info))))
            self.connection.sendall(str.encode(info))
        else:
            self.connection.send(info.encode())
        BUFFER_SIZE = 4096

        with pathlib.Path(dir_path + "/" + self.filename).open("wb") as f:
            while True:

                bytes_read = self.connection.recv(BUFFER_SIZE)
                if len(bytes_read) < BUFFER_SIZE:
                    break
                f.write(bytes_read)
                print(1)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = PyQt6.QtWidgets.QApplication(sys.argv)
    path = str(pathlib.Path(__file__).parent.resolve()) + "/fonts/jetbrains.ttf"
    PyQt6.QtGui.QFontDatabase.addApplicationFont(path)
    ex = start_window()
    app.setFont(PyQt6.QtGui.QFont('JetBrains Mono NL'))
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
