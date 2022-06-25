# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import QApplication
import time

from PyQt5.QtCore import QThread, pyqtSignal

import tools as local_handler
from module import MainWindow, InputWindow, ProgressWindow
from file_socket import Handler, FileIO
from base_socket import BaseSocket
import sys
import socket

#import Ui_Dialog as login_Ui
#from netdisk_re import Ui_Form as re_Ui
from PyQt5.QtWidgets import QMessageBox

from register1 import Ui_RegisterWin as re_Ui
from login1 import Ui_LoginWin as login_Ui
from main_window import Ui_Form as main_Ui
import socket

import main


'''
class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(811, 559)

        #左半背景
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(90, 100, 231, 341))
        self.label.setStyleSheet("background-color: rgb(228, 255, 246);")
        self.label.setText("")
        self.label.setObjectName("label")
        #右半背景
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(300, 100, 431, 341))
        self.label_2.setStyleSheet("background-image: url(:/images/2.jpg);")
        self.label_2.setObjectName("label_2")

        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(120, 160, 151, 51))

        #欢迎光临
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(20)

        #帐号密码线
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(120, 240, 141, 21))
        self.lineEdit.setStyleSheet("border:none;\n"
"background-color: rgb(228, 255, 246);\n"
"border-bottom:2px solid rgba(0,0,0,100);")
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_2.setGeometry(QtCore.QRect(120, 300, 141, 21))
        self.lineEdit_2.setStyleSheet("border:none;\n"
"background-color: rgb(228, 255, 246);\n"
"border-bottom:2px solid rgba(0,0,0,100);")
        self.lineEdit_2.setObjectName("lineEdit_2")

        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(110, 370, 81, 41))
        self.pushButton.setObjectName("pushButton")

        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(200, 370, 81, 41))
        self.pushButton_2.setObjectName("pushButton_2")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_2.setText(_translate("Dialog", "TextLabel"))
        self.label_3.setText(_translate("Dialog", "欢迎登录"))
        self.lineEdit.setPlaceholderText(_translate("Dialog", "账号："))
        self.lineEdit_2.setPlaceholderText(_translate("Dialog", "密码："))

        self.pushButton.setText(_translate("Dialog", "确定"))
        self.pushButton_2.setText(_translate("Dialog", "注册"))
import res_rc
'''
class login_Thread(QThread):
    #自定义信号声明
    # 使用自定义信号和UI主线程通讯，参数是发送信号时附带参数的数据类型，可以是str、int、list等
    finishSignal = pyqtSignal(int)

    # 带一个参数t
    def __init__(self, t,parent=None):
        super(login_Thread, self).__init__(parent)

        self.t = t
    #run函数是子线程中的操作，线程启动后开始执行
    def run(self):
        for i in range(self.t):
            time.sleep(1)
            #发射自定义信号
            #通过emit函数将参数i传递给主线程，触发自定义信号
            self.finishSignal.emit(str(i))




def create_socket(addr, protocol_len):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect(addr)
    print(f"与 {addr} 连接成功")
    return BaseSocket(s, addr, protocol_len)





'''
    app = QtWidgets.QApplication(sys.argv)  # 创建一个QApplication，也就是你要开发的软件app
    MainWindow = QtWidgets.QMainWindow()    # 创建一个QMainWindow，用来装载你需要的各种组件、控件
    ui = Ui_Dialog()                    # ui是Ui_MainWindow()类的实例化对象
    ui.setupUi(MainWindow)                  # 执行类中的setupUi方法，方法的参数是第二步中创建的QMainWindow
    MainWindow.show()                       # 执行QMainWindow的show()方法，显示这个QMainWindow
    sys.exit(app.exec_())                   # 使用exit()或者点击关闭按钮退出QApplication///
    '''


class lr_button:

    def on_pushButton_register_clicked1(self):
        account1 = self.re_user.text()
        password1 = self.re_passwd.text()
        return 'event=login\naccount='+account1+'\npasswd='+password1+'\n'   #暂定


if __name__ == "__main__":


    app = QtWidgets.QApplication(sys.argv)
    #app = QApplication(sys.argv)
    addr=('192.168.42.230',4000)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect(addr)




    global my_isLogin
    my_isLogin=0
    global my_isRegister
    my_isRegister=0
    class LoginWindow(QtWidgets.QMainWindow, login_Ui):
       switch_window1 = QtCore.pyqtSignal()  # 跳转信号
       switch_window2 = QtCore.pyqtSignal()  # 跳转信号
       # 信号槽机制：设置一个信号，用于触发接收区写入动作
       signal_write_msg = QtCore.pyqtSignal(str)

       def __init__(self):
           self.flag = 0
           super(LoginWindow, self).__init__()
           self.setupUi(self)
           self.register_2.clicked.connect(self.goRegister)
           # self.register_2.clicked.connect(LoginWindow.close)

           self.login.clicked.connect(self.on_pushButton_login_clicked1)

           self.login.clicked.connect(self.goMain)


       def goRegister(self):
           # LoginWindow.close()
           self.switch_window1.emit()

       def goMain(self):
           self.switch_window2.emit()

       def on_pushButton_login_clicked1(self):
           # self.socket_open_tcpc()

            account1 = self.user.text()
            password1 = self.passwd.text()
            test_str = ''
            if account1 != '' and password1 != '':
                test_str = 'event=login\naccount=' + account1 + '\npasswd=' + password1 + '\n'  # 暂定
            else:
                test_str=''
                reply = QMessageBox.warning(self, "警告", "账号密码不能为空，请输入！")
                return
            s.send(test_str.encode())




    class RegisterWindow(QtWidgets.QMainWindow, re_Ui):
        switch_window3 = QtCore.pyqtSignal()  # 跳转信号

        def __init__(self):
           super(RegisterWindow, self).__init__()
           self.setupUi(self)
           self.back.clicked.connect(self.goLogin)
           self.yes.clicked.connect(self.on_pushButton_register_clicked1)

        def goLogin(self):
           self.switch_window3.emit()

        def on_pushButton_register_clicked1(self):
           # self.socket_open_tcpc()
            account1 = self.re_user.text()
            password1 = self.re_passwd.text()
            test_str = ''
            if account1 != '' and password1 != '':
                test_str = 'event=register\naccount=' + account1 + '\npasswd=' + password1 + '\n'  # 暂定
            else:
                test_str=''
                reply = QMessageBox.warning(self, "警告", "账号密码不能为空，请输入！")
                return
            s.send(test_str.encode())

            str = s.recv(1024)
            if 'accepted' in str.decode():
                my_isRegister = 1
                print(my_isRegister)
                reply = QMessageBox.warning(self, "恭喜", "注册成功")


    class MainWindow_(QtWidgets.QMainWindow, main_Ui):
        def __init__(self):
           super(MainWindow_, self).__init__()
           self.setupUi(self)


    class Controller(login_Ui, main_Ui, re_Ui):
        def __init__(self):
           self.register = RegisterWindow()
           self.login_ = LoginWindow()
           self.main = MainWindow_()


        def show_login(self):
           self.register.close()
           # self.login_ = LoginWindow()
           self.login_.switch_window1.connect(self.show_register)
           self.login_.switch_window2.connect(self.show_main)
           self.login_.close()
           self.login_.show()

        # 跳转到 operate 窗口, 注意关闭原页面
        def show_register(self):
           self.login_.close()

           # self.register = RegisterWindow()
           self.register.switch_window3.connect(self.show_login)
           self.register.close()
           self.register.show()

        def show_main(self):
           str = s.recv(1024)
           print(str)
           if 'accepted' in str.decode():
                my_isLogin = 1
                print(my_isLogin)
                self.login_.close()
                #self.main.close()
                #self.main.show()


                #app = QApplication(sys.argv)
                # 服务器的IP Port
                '''ip = '192.168.42.230'
                port = 4000
                addr = (ip, port)
                addr2 = ('8.130.23.63', 6000)'''
                # 协议的长度（不用于文件流的传送）
                p_len = 1024

                # 下载的时候一次接受多少字节
                once_recv_btyes = 10240

                # 发送文件的时候一次读多少字节
                once_recv_file_bytes = 10240

                # 创建socket核心
                Session = BaseSocket(s, addr, p_len)

                # 控制类（根据协议实作出响应）
                remote_handler = Handler(Session, FileIO, p_len, once_recv_file_bytes, once_recv_btyes)

                # 注册session的响应类
                Session.on_msg = remote_handler.on_msg

                # 启动session监听
                Session.recv_data_for_every()

                # 实例主窗口的子组件（交互输入框、进度展示界面）
                input_window = InputWindow()
                progress = ProgressWindow()

                # 实例化主窗口（文件窗口的主窗口）
                main_window = MainWindow(local_handler, remote_handler,
                                         local_handler.Dict(input_window=input_window, progress_window=progress))

                # 注册控制类的回调函数
                remote_handler.local_reload = MainWindow.local_reload_table
                remote_handler.show_progress = MainWindow.show_progress  # 信号槽
                remote_handler.hide_progress = MainWindow.hide_progress
                remote_handler.set_status = MainWindow.set_progress

                # 注册进度条关闭的时间
                progress.on_close = MainWindow.on_progress_window_close
                time.sleep(0.5)  # 设置时间延迟，以表示运行时间长短
                main_window.show()
           else:
               self.show_login()




    controller = Controller()  # 控制器实例
    controller.show_login()

    sys.exit(app.exec_())
