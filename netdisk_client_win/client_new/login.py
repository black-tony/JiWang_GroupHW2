# -*- coding: gbk -*-
import socket
import hashlib
from PyQt5 import QtCore, QtWidgets
import sys
from CONST import HOST, PORT
# import tools

class LoginInterface(object):
    def __init__(self):
        self.account = ""

    def login_interface(self):
        self.window = QtWidgets.QWidget()
        self.window.setWindowTitle("��¼")
        self.window.resize(500, 500)

        account_label = QtWidgets.QLabel(self.window)
        passwd_label = QtWidgets.QLabel(self.window)
        self.account_line = QtWidgets.QLineEdit(self.window)
        self.passwd_line = QtWidgets.QLineEdit(self.window)
        login_btn = QtWidgets.QPushButton(self.window)
        register_btn = QtWidgets.QPushButton(self.window)

        account_label.move(0, 0)
        self.account_line.move(60, 0)
        passwd_label.move(0, 30)
        self.passwd_line.move(60, 30)
        login_btn.move(120,60)
        register_btn.move(0, 60)

        account_label.setText("�û���: ")
        passwd_label.setText("����: ")
        login_btn.setText("��¼")
        register_btn.setText("ע��")

        self.passwd_line.setEchoMode(QtWidgets.QLineEdit.Password)


        login_btn.clicked.connect(self.handle_login)
        register_btn.clicked.connect(self.handle_register)
        self.window.show()

        return self.account

    def handle_login(self):
        self.account = self.account_line.text().strip()
        self.passwd = self.passwd_line.text().strip()
        event = bytes("event=login\naccount=" + self.account + "\npasswd=" + self.passwd + "\n", encoding="gbk")
        # print("account={!r}".format(event))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST,PORT))
        s.sendall(event)
        response = s.recv(1024)
        s.close()
        list = response.split(b"\n")
        if list[0] == b"failed":
            QtWidgets.QMessageBox.critical(
                self.window,
                "��¼ʧ��",
                bytes.decode(list[1], "gbk")
            )
            return
        # print("account={!r}".format(self.account))
        self.window.close()
    
    def handle_register(self):
        self.account = self.account_line.text().strip()
        self.passwd = self.passwd_line.text().strip()
        event = bytes("event=register\naccount=" + self.account + "\npasswd=" + self.passwd + "\n", encoding="gbk")

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST,PORT))
        s.sendall(event)
        response = s.recv(1024)
        print(response)
        s.close()
        list = response.split(b"\n")
        if list[0] == b"failed":
            QtWidgets.QMessageBox.critical(
                self.window,
                "ע��ʧ��",
                bytes.decode(list[1], "gbk")
            )
            return
        else:
            QtWidgets.QMessageBox.information(
                self.window,
                "ע��ɹ�",
                bytes.decode(list[1], "gbk")
            )
            return
    