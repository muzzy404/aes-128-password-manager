""" Password Manager main QT window module. """
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
from PyQt5.QtWidgets import QInputDialog

from aes import aes
from aes.transformations import apply_key_constraints as aes_password_constraints
from controller.alerts import show_info_window, show_confirmation_window


class PasswordManager(QMainWindow):
    """
    PasswordManager main window.
    """
    def closeEvent(self, *args, **kwargs):
        super().closeEvent(*args, **kwargs)
        self.database.save_data(self.records)

    def __init__(self):
        """
        PasswordManager init function.
        """
        super().__init__()
        uic.loadUi('./view/main_window.ui', self)
        self.clipboard_free = True
        self.database, self.records = self.open_database()
        self.init_ui()

    def open_database(self):
        """
        Method to open existing database or create new.

        :return: database file and records list
        :rtype: tuple
        """
        db_name, ok = QInputDialog.getText(self, 'Database name', 'Name:')
        if not ok:
            raise RuntimeError

        while True:
            password, ok = QInputDialog.getText(self, '"{}" database password'.format(db_name), 'Password:',
                                                QLineEdit.Password)
            if ok:
                try:
                    database = PasswordsFile(password=password, file_name=db_name, pwd='./db/')
                    records = database.load_data()
                    return database, records
                except Exception as error:
                    show_info_window('Incorrect password', 'Please try another password.', details=str(error))
                    continue
            else:
                raise RuntimeError

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

        self.insert_records_to_table()

    def add_button_click_listener(self):
        """
        Add button click listener.
        """
        try:
            record = Record(title=self.input_title.text(),
                            username=self.input_username.text(),
                            password=self.input_password.text(),
                            destination=self.input_type.text())
        except ValueError:
            show_info_window('Some fields do not contain data', 'Please fill all fields to add new record.')
            return
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
                                    'Record "{}" will be deleted. Press OK to continue.'.format(record.title)):
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
        if any(len(item) == 0 for item in [title, username, password, destination]):
            raise ValueError('record init got empty strings')
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
    """
    PasswordsFile class to work with password manager file.
    """
    __FILE_NAME = 'passwords'

    def __init__(self, password, file_name=None, pwd='../db/'):
        """
        PasswordsFile initialization.

        :param password: database password
        :type password: str
        :param file_name: database name
        :type file_name: str
        :param pwd: path to file
        :type pwd: str
        """
        aes_password_constraints(password)
        self.db_file = pwd + (file_name if file_name else self.__FILE_NAME)
        self.password = password

    def load_data(self):
        """
        Method to load data from encrypted file.

        :return: list of records from database file
        :rtype: list
        """
        if Path(self.db_file).exists():
            with open(self.db_file, 'rb') as f:
                bytes_data = f.read()
                raw_data = bytes_data.decode()
            f.close()

            encrypted_blocks = aes.message_to_bytes(raw_data)
            decrypted_blocks = []
            for block in encrypted_blocks:
                decrypted_blocks.append(aes.decrypt(block, self.password))
            decrypted_string = aes.blocks_to_message(decrypted_blocks)
            items = decrypted_string.split(',')[:-1]

            if len(raw_data) > 0 and len(items) == 0:
                raise PermissionError('access to db denied (1)')
            if len(items) % 4 != 0:
                raise PermissionError('access to db denied (2)')

            records = []
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
        """
        Method to encrypt and save encrypted data to file.

        :param records:
        :return:
        """
        # delete database file if no records
        if len(records) == 0:
            if Path(self.db_file).exists():
                os.remove(self.db_file)
            return

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

        with open(self.db_file, 'wb') as f:
            bytes_data = encrypted.encode()
            f.write(bytes_data)
        f.close()
