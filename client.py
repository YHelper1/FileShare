import socket, start_client, PyQt6.QtWidgets, sys, PyQt6.QtGui
import pathlib, connect_
from threading import Thread
def read_props():
    f = open("properties.txt", "r")
    mas = []
    for i in f.readlines():
        mas.append(i[i.find(" ") + 1:].rstrip('\n'))
    f.close()
    return mas


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
        self.pushButton.clicked.connect(self.load)

    def open_settings(self):
        self.wind = settings_window()
        self.wind.show()

    def load(self):
        self.loadwind = load_file()
        self.loadwind.show()

class load_file(PyQt6.QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Загрузка файла")
        self.setFixedSize(300, 200)
        self.progress_bar = PyQt6.QtWidgets.QProgressBar(self)
        self.progress_bar.move(0, 50)
        #self.progress_bar.setRange(0, 100)
        Thread(self.send_f()).run()
    def send_f(self):
        file = PyQt6.QtWidgets.QFileDialog.getOpenFileName(self)[0]
        input_file = open(file, "rb")
        data = input_file.read()
        print(len(data))
        input_file.close()
        ip = read_props()[0]
        port = read_props()[1]
        connection = connect_.connect_(ip, int(port))
        connection.sendfile(data)

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
