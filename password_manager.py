from PyQt5 import QtCore, QtGui, QtWidgets, uic


class PasswordManager(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('./view/main_window.ui', self)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = PasswordManager()
    window.show()
    sys.exit(app.exec_())
