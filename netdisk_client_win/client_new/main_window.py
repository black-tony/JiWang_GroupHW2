# -*- coding: gbk -*-
import socket
import hashlib
from turtle import done
from PyQt5 import QtCore, QtWidgets
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QInputDialog

from CONST import HOST, PORT
# import tools
from sub_window import Ui_widget


DEBUG = 1


class MainInterface(object,):

    def __init__(self, account):

        self.setupUi()

        self.account = account
        self.pdir = "/"
        
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
        self.file_layout = QtWidgets.QVBoxLayout()



    def setupUi(self):
        self.window = QtWidgets.QWidget()
        self.window.setWindowTitle("网盘")
        self.window.resize(1000, 600)

        self.refresh_btn = QtWidgets.QPushButton()
        self.refresh_btn.setText("刷新")

        self.newfolder_btn = QtWidgets.QPushButton()
        self.newfolder_btn.setText("新建文件夹")

        self.paste_btn = QtWidgets.QPushButton()
        self.paste_btn.setText("粘贴")


    def main_interface(self):
        self.window = QtWidgets.QWidget()
        self.window.setWindowTitle("网盘")
        self.window.resize(1000, 600)

        # 大布局
        # self.main_layout.move(0, 200)
        top_bar_layout = QtWidgets.QHBoxLayout()

        refresh_btn = QtWidgets.QPushButton()
        refresh_btn.setText("刷新")

        newfolder_btn = QtWidgets.QPushButton()
        newfolder_btn.setText("新建文件夹")

        paste_btn = QtWidgets.QPushButton()
        paste_btn.setText("粘贴")

        top_bar_layout.addWidget(refresh_btn)
        top_bar_layout.addWidget(newfolder_btn)
        top_bar_layout.addWidget(paste_btn)

        self.main_layout.addLayout(top_bar_layout)
        self.main_layout.addLayout(self.file_layout)
        self.getList()

        self.window.show()
        refresh_btn.clicked.connect(self.getList)
        newfolder_btn.clicked.connect(self.main_mkdir)
        #self.refresh_btn.clicked(self.getList)

    def clearFileLayout(self,layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearFileLayout(item.layout())

        '''item_list = list(range(self.file_layout.count()))
        if DEBUG:
            print(item_list)

        for i in item_list:
            line_layout = self.file_layout.itemAt(i)
            print(line_layout)
            self.file_layout.removeItem(line_layout)
            if line_layout==None:
                break

            print('&&')
            line_layout.widget().deleteLater()
            for i in range(line_layout):
                item = line_layout.itemAt(i)
                line_layout.removeItem(item)
                if item.widget():
                    item.widget().deleteLater()
            self.file_layout.removeItem(line_layout)
            if line_layout.layout():
                line_layout.layout().deleteLater()'''


    def getList(self):
        event = bytes("event=list\naccount=" + self.account + "\npdir=" + self.pdir + "\n", encoding="gbk")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST,PORT))
        s.sendall(event)
        response = s.recv(4096)
        s.close()
        if DEBUG:
            print(response)

        list = response.split(b"\n")
        if list[0] == b"failed":
            QtWidgets.QMessageBox.critical(
                self.window,
                "获取文件列表失败",
                bytes.decode(list[1], "gbk")
            )
            return
        file_list = []
        for i in list:
            k = bytes.decode(i, "gbk")
            if len(k) >= 2 and (k[0] == 'f' or k[0] == 'd') and k[1] == ' ':
                print(k)
                file_list.append(k)

        self.clearFileLayout(self.file_layout)
        for file in file_list:
            line_layout = QtWidgets.QHBoxLayout()
            type_label = QtWidgets.QLabel()
            if file[0] == 'd':
                type_label.setText("文件夹")
            else:
                type_label.setText("文件  ")
            name_label = QtWidgets.QLabel()
            name_label.setText(file[2:])
            if file[0] == 'd':
                enter_btn = QtWidgets.QPushButton()
                enter_btn.setText("进入")
                line_layout.addWidget(enter_btn)
            
            copy_btn = QtWidgets.QPushButton()
            copy_btn.setText("复制")
            move_btn = QtWidgets.QPushButton()
            move_btn.setText("剪切")
            delete_btn = QtWidgets.QPushButton()
            delete_btn.setText("删除")
            download_btn = QtWidgets.QPushButton()
            download_btn.setText("下载")

            line_layout.addWidget(type_label)
            line_layout.addWidget(name_label)
            line_layout.addWidget(copy_btn)
            line_layout.addWidget(move_btn)
            line_layout.addWidget(delete_btn)
            line_layout.addWidget(download_btn)
            line_layout.setContentsMargins(0,0,0,0)
            line_layout.setSpacing(1)
            
            self.file_layout.addLayout(line_layout)

        print(self.file_layout.count())
        self.window.setLayout(self.main_layout)


    ##刷新
    def main_mkdir(self,package):
        file_text=QInputDialog.getText(None, "新建文件夹", "请输入新文件夹名称")  #对话框

        print(file_text)
        filename=str(file_text[0])
        mkdir_msg='event=mkdir\naccount='+self.account+'\npdir='+self.pdir+'\nname='+filename+'\n'
        print(mkdir_msg)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        s.sendall(mkdir_msg.encode('gbk'))
        response = s.recv(4096)
        s.close()
        print(response)