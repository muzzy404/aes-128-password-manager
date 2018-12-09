""" Password Manager main window module. """
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QTableWidgetItem


class PasswordManager(QMainWindow):
    """
    PasswordManager main window.
    """
    def __init__(self):
        """
        PasswordManager init function.
        """
        super().__init__()
        uic.loadUi('./view/main_window.ui', self)
        self.init_ui()

        self.insert_records_to_table(self.__get_test_records())
        self.insert_record_to_table(Record('new', 'new', 'new', 'new'))
        # self.clear_table()

    def insert_records_to_table(self, records):
        """
        Method to set records list to table.

        :param records: records for table
        :type records: list
        """
        for record in records:
            self.insert_record_to_table(record)

    def insert_record_to_table(self, record):
        """
        Method to add one record to table.

        :param record: record for table
        :type record: Record
        """
        row = self.table_passwords.rowCount()
        cells = self.__get_dict_from_record(record)

        self.table_passwords.insertRow(row)
        for cell in cells:
            self.table_passwords.setItem(row, cell, QTableWidgetItem(cells[cell]))

    def clear_table(self):
        """
        Method to clear table.
        """
        for i in reversed(range(self.table_passwords.rowCount())):
            self.table_passwords.removeRow(i)

    def init_ui(self):
        """
        Method for UI initialization.
        """
        self.input_password.setEchoMode(QLineEdit.Password)
        self.table_passwords.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        titles = self.__get_headers_tips()
        for i in titles.keys():
            self.table_passwords.horizontalHeaderItem(i).setToolTip(titles[i])

    @staticmethod
    def __get_dict_from_record(record, show_password=False):
        """
        Static method to convert record to dict with pairs: cell number <-> cell content

        :param record: record to convert
        :type record: Record
        :param show_password: flag to show password or use '*' characters instead
        :type show_password: bool
        :return: converted record
        :rtype: dict
        """
        return {
            0: record.title,
            1: record.username,
            2: record.password if show_password else '*' * 6,
            3: record.destination,
        }

    @staticmethod
    def __get_headers_tips():
        """
        Static method to get tips for headers, pars: header number <-> tip content

        :return: tips
        :rtype: dict
        """
        return {
            0: "record title",
            1: "username, ip address, etc.",
            2: "password, secret word",
            3: "url, ssh, etc."
        }

    @staticmethod
    def __get_test_records():
        """
        Static method to get test records.

        :return: list of records
        :rtype: list
        """
        records = [Record('record 1', 'user 1', 'password_1', 'vk.com'),
                   Record('record 2', 'user 2', 'password_2', 'ssh 127.0.0.1'),
                   Record('record 3', 'user 3', 'password_3', 'telegram')]
        return records


class Record:
    def __init__(self, title, username, password, destination):
        self.title = title
        self.username = username
        self.password = password
        self.destination = destination
