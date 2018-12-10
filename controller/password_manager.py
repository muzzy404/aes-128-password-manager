""" Password Manager main window module. """
import os
from pathlib import Path

import pyperclip
from threading import Thread
from time import sleep

from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QTableWidgetItem

from aes import aes
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
        self.setWindowIcon(QtGui.QIcon('./controller/key_icon.png'))

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


class PasswordsFile:
    __FILE_NAME = 'passwords'

    def __init__(self, password='testtest', file_name=None, pwd='../db/'):
        self.db_file = pwd + (file_name if file_name else self.__FILE_NAME)
        self.password = password

    def load_data(self, given_data):
        if Path(self.db_file).exists():
            with open(self.db_file, 'r', encoding="utf8") as f:
                raw_data = f.read()  # given_data

                for i in range(len(given_data)):
                    if raw_data[i] != given_data[i]:
                        print('{}: "{}" - "{}"'.format(i, repr(raw_data[i]), repr(given_data[i])))

                print(len(raw_data), len(given_data))
                if raw_data == given_data:
                    print('==')
                else:
                    print('!=')
            f.close()

            encrypted_blocks = aes.message_to_bytes(raw_data)
            decrypted_blocks = []
            for block in encrypted_blocks:
                decrypted_blocks.append(aes.decrypt(block, self.password))
            decrypted_string = aes.blocks_to_message(decrypted_blocks)

            records = []
            items = decrypted_string.split(',')[:-1]

            row = []
            for item in items:
                row.append(item)
                if len(row) == 4:
                    records.append(Record(title=row[0], username=row[1], password=row[2], destination=row[3]))
                    row = []

            return records
        else:
            return []

    def save_data(self, records):
        data = ''
        for record in records:
            data += '{title},{name},{password},{type},'.format(title=record.title,
                                                               name=record.username,
                                                               password=record.password,
                                                               type=record.destination)
        blocks = aes.message_to_blocks(data)
        encrypted_blocks = []
        for block in blocks:
            encrypted_blocks.append(aes.encrypt(block, self.password))
        encrypted = aes.blocks_to_message(encrypted_blocks)

        with open(self.db_file, 'wt', encoding="utf8") as f:
            f.write(encrypted)
        f.close()

        return encrypted


# tets
passwords_file = PasswordsFile()
en = passwords_file.save_data([Record('11__1111_11', 'name1', 'password1', 'type1'),
                               Record('title2', 'name2', 'password2', 'type2'),
                               Record('lafffffff__fffffla', 't', 'aaa', '111'),
                               Record('laffff****ff_fffffffla', 't', 'aaa', '111'),
                               Record('123!*123', '+__$$$$#%#@%#@t', 'aaa', '111'),
                               Record('laffffffff*fffffla', 't', 'aaa', '111'),
                               Record('laffffffff*fffffla', 't', 'aaa', '111'),
                               Record('title3', '567567567', 'password3', 'typetype3'),])
d = passwords_file.load_data(en)
for i in d:
    print(i)
