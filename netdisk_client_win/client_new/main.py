# -*- coding: gbk -*-
from PyQt5 import QtCore, QtWidgets
import sys
from login import LoginInterface
from CONST import HOST, PORT
from main_window import MainInterface


if __name__ =="__main__":

    app = QtWidgets.QApplication(sys.argv)

    # 登录界面
    li = LoginInterface()

    account = li.login_interface()
    print(account)

    app.exec_()
    account = '123456'
    # 方便调试的话,把登录界面的三行注释掉,放开account的注释
    if account:
        mi = MainInterface(account)
        mi.main_interface()

    app.exec_()
    sys.exit()