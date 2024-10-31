import socket, start_client, PyQt6.QtWidgets, sys, PyQt6.QtGui
import pathlib, connect_

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
        self.setFixedSize(300, 250)
        self.lbl1 = PyQt6.QtWidgets.QLabel(self)
        self.lbl1.setText('Ip')
        self.lbl1.move(120, 0)
        self.ip = PyQt6.QtWidgets.QLineEdit(self)
        self.ip.move(100, 40)
        self.lbl2 = PyQt6.QtWidgets.QLabel(self)
        self.lbl2.setText('Порт')
        self.lbl2.move(120, 80)
        self.port = PyQt6.QtWidgets.QLineEdit(self)
        self.port.move(100, 120)
        self.confirm = PyQt6.QtWidgets.QPushButton(self)
        self.confirm.move(100, 180)
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
        self.settings.setIcon(PyQt6.QtGui.QIcon('settings.png'))
        self.settings.resize(40, 40)
        self.settings.move(420, 0)
        self.settings.clicked.connect(self.open_settings)

    def open_settings(self):
        self.wind = settings_window()
        self.wind.show()

class load_file(PyQt6.QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        file = PyQt6.QtWidgets.QFileDialog.getOpenFileName(self)[0]
        input_file = open(file, "rb")
        data = input_file.read()
        input_file.close()
        ip = read_props()[0]
        port = read_props()[1]
        connection = connect_.connect_(ip, port)
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
