""" Main module to run application. """
import sys
from PyQt5.QtWidgets import QApplication
from controller.password_manager import PasswordManager

if __name__ == '__main__':
    app = QApplication(sys.argv)
    try:
        window = PasswordManager()
        window.show()
        sys.exit(app.exec_())
    except RuntimeError:
        app.exit(0)
