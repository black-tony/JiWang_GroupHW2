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
        self.window.setWindowTitle("登录")
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

        account_label.setText("用户名: ")
        passwd_label.setText("密码: ")
        login_btn.setText("登录")
        register_btn.setText("注册")

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
                "登录失败",
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
                "注册失败",
                bytes.decode(list[1], "gbk")
            )
            return
        else:
            QtWidgets.QMessageBox.information(
                self.window,
                "注册成功",
                bytes.decode(list[1], "gbk")
            )
            return
    