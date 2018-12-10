""" Module with functions to show different QT alerts. """
from PyQt5.QtWidgets import QMessageBox


def show_info_window(title, information, details=None):
    """
    Function to show information window.

    :param title: text title inside of alert box
    :type title: str
    :param information: message inside of alert box
    :type information: str
    :param details: additional details
    :type details: str
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Information")
    msg.setText(title)
    msg.setInformativeText(information)
    if details is not None:
        msg.setDetailedText(details)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


def show_confirmation_window(title, information):
    """
    Function to show confirmation window.

    :param title: text title inside of alert box
    :type title: str
    :param information: message inside of alert box
    :type information: str
    :return: confirmation
    :rtype: bool
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("Warning")
    msg.setText(title)
    msg.setInformativeText(information)
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    return True if msg.exec_() == QMessageBox.Ok else False
