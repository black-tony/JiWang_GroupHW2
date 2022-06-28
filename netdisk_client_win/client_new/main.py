# -*- coding: gbk -*-
from PyQt5 import QtCore, QtWidgets
import sys
from login import LoginInterface
from CONST import HOST, PORT
from main_window import MainInterface


if __name__ =="__main__":

    app = QtWidgets.QApplication(sys.argv)

    # ��¼����
    li = LoginInterface()

    account = li.login_interface()
    print(account)

    app.exec_()
    account = '123456'
    # ������ԵĻ�,�ѵ�¼���������ע�͵�,�ſ�account��ע��
    if account:
        mi = MainInterface(account)
        mi.main_interface()

    app.exec_()
    sys.exit()