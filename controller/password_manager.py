""" Password Manager main window module. """
import pyperclip
from threading import Thread
from time import sleep

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QTableWidgetItem

from controller.alerts import show_info_window, show_confirmation_window


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
        self.records = []
        self.clipboard_free = True
        self.init_ui()

    def init_ui(self):
        """
        Method for UI initialization.
        """
        self.input_password.setEchoMode(QLineEdit.Password)
        self.table_passwords.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        titles = self.__get_headers_tips()
        for i in titles.keys():
            self.table_passwords.horizontalHeaderItem(i).setToolTip(titles[i])

        self.button_add.clicked.connect(lambda: self.add_button_click_listener())
        self.button_copy.clicked.connect(lambda: self.copy_button_click_listener())
        self.button_delete.clicked.connect(lambda: self.delete_button_click_listener())

        self.records.extend(self.__get_test_records())
        self.insert_records_to_table()

    def add_button_click_listener(self):
        """
        Add button click listener.
        """
        record = Record(title=self.input_title.text(),
                        username=self.input_username.text(),
                        password=self.input_password.text(),
                        destination=self.input_type.text())
        self.clear_all_inputs()
        self.records.append(record)
        self.insert_record_to_table(record)

    def copy_button_click_listener(self):
        """
        Copy button click listener.
        """
        if not self.clipboard_free:
            show_info_window('Please wait...', 'Clipboard will be cleaned soon to copy another password')
            return

        index = self.__get_index_of_selected()
        if index == self.__NO_SELECTED:
            show_info_window('No row selected', 'Select any row to copy password to clipboard')
            return
        if index == self.__FEW_SELECTED:
            show_info_window('More than one row selected', 'Select only one row to copy password to clipboard')
            return

        record = self.records[index]
        self.__copy_to_clipboard(record.password)

    def delete_button_click_listener(self):
        """
        Delete button click listener.
        """
        index = self.__get_index_of_selected()
        if index == self.__NO_SELECTED:
            show_info_window('No row selected', 'Select any row to delete record')
            return
        if index == self.__FEW_SELECTED:
            show_info_window('More than one row selected', 'Select only one row to delete record')
            return

        record = self.records[index]
        if show_confirmation_window('Confirm record deleting',
                                    'Do you what to delete "{}" record'.format(record.title)):
            del self.records[index]
            self.clear_table()
            self.insert_records_to_table()

    def insert_records_to_table(self, records=None):
        """
        Method to set records list to table.

        :param records: records for table
        :type records: list
        """
        if records is None:
            records = self.records
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

    def clear_all_inputs(self):
        """
        Method to clear all input fields.
        """
        self.input_title.clear()
        self.input_username.clear()
        self.input_password.clear()
        self.input_type.clear()

    def __get_index_of_selected(self):
        """
        Private method ro get selected row index.

        :return: index of selected row or status
        :rtype: int
        """
        indexes = self.table_passwords.selectionModel().selectedRows()
        if len(indexes) == 0:
            return self.__NO_SELECTED
        if len(indexes) > 1:
            return self.__FEW_SELECTED
        return indexes[0].row()

    def __copy_to_clipboard(self, text, sec=5):
        """
        Private method to copy text to clipboard for specific time period (sec) and clear clipboard in the end.

        :param text: text to copy to clipboard
        :type text: str
        :param sec: period for clipboard clearing
        :type sec: int
        """
        def clear_clipboard():
            self.clipboard_free = False
            message = 'Clipboard will be cleared in {} second{}...'
            for i in reversed(range(1, sec + 1)):
                self.statusbar.showMessage(message.format(i, 's') if i > 1 else message.format(i, ''))
                sleep(1)
            pyperclip.copy('')
            self.statusbar.showMessage('')
            self.clipboard_free = True

        pyperclip.copy(text)
        thread = Thread(target=clear_clipboard)
        thread.start()

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

    __NO_SELECTED = -1
    __FEW_SELECTED = -2


class Record:
    """
    Record class to perform table and file record.
    """
    def __init__(self, title, username, password, destination):
        """
        Record initialization.

        :param title: title of record
        :type title: str
        :param username: username
        :type username: str
        :param password: password
        :type password: str
        :param destination: type (url, ssh, etc.)
        :type destination: str
        """
        self.title = title
        self.username = username
        self.password = password
        self.destination = destination

    def __repr__(self):
        rec = 'title: ' + self.title + ', '
        rec += 'username: ' + self.username + ', '
        rec += 'password: ' + self.password + ', '
        rec += 'destination: ' + self.destination
        return rec
