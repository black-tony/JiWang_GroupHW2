# -*- coding: cp936 -*-

# Form implementation generated from reading ui file 'upload.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
import sys

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1049, 682)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.RemoteComboBox = QtWidgets.QComboBox(Form)
        self.RemoteComboBox.setEnabled(True)
        self.RemoteComboBox.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(11)

        self.RemoteComboBox.setFont(font)
        self.RemoteComboBox.setEditable(True)
        self.RemoteComboBox.setObjectName("RemoteComboBox")

        self.gridLayout.addWidget(self.RemoteComboBox, 0, 3, 1, 1)
        self.RemoteLastDir = QtWidgets.QPushButton(Form)
        self.RemoteLastDir.setMaximumSize(QtCore.QSize(70, 40))
        self.RemoteLastDir.setObjectName("RemoteLastDir")
        self.gridLayout.addWidget(self.RemoteLastDir, 0, 4, 1, 1)
        self.RemoteFiles = QtWidgets.QTableWidget(Form)
        self.RemoteFiles.setObjectName("RemoteFiles")
        self.RemoteFiles.setColumnCount(0)
        self.RemoteFiles.setRowCount(0)
        self.gridLayout.addWidget(self.RemoteFiles, 1, 3, 1, 3)
        self.LocalComboBox = QtWidgets.QComboBox(Form)
        self.LocalComboBox.setEnabled(True)
        self.LocalComboBox.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(11)

        self.LocalComboBox.setFont(font)
        self.LocalComboBox.setAcceptDrops(False)
        self.LocalComboBox.setToolTip("")
        self.LocalComboBox.setEditable(True)
        self.LocalComboBox.setObjectName("LocalComboBox")

        self.gridLayout.addWidget(self.LocalComboBox, 0, 0, 1, 1)
        self.DowLoad = QtWidgets.QPushButton(Form)
        self.DowLoad.setMaximumSize(QtCore.QSize(70, 40))
        self.DowLoad.setObjectName("DowLoad")
        self.gridLayout.addWidget(self.DowLoad, 0, 5, 1, 1)
        self.LocalFiles = QtWidgets.QTableWidget(Form)
        self.LocalFiles.setObjectName("LocalFiles")
        self.LocalFiles.setColumnCount(0)
        self.LocalFiles.setRowCount(0)
        self.gridLayout.addWidget(self.LocalFiles, 1, 0, 1, 3)
        self.LocalLastDir = QtWidgets.QPushButton(Form)
        self.LocalLastDir.setMaximumSize(QtCore.QSize(70, 40))
        self.LocalLastDir.setObjectName("LocalLastDir")
        self.gridLayout.addWidget(self.LocalLastDir, 0, 1, 1, 1)
        self.UpLoad = QtWidgets.QPushButton(Form)
        self.UpLoad.setMaximumSize(QtCore.QSize(70, 40))
        self.UpLoad.setObjectName("UpLoad")
        self.gridLayout.addWidget(self.UpLoad, 0, 2, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.RemoteLastDir.setText(_translate("Form", "上一级"))
        self.DowLoad.setText(_translate("Form", "下载"))
        self.LocalLastDir.setText(_translate("Form", "上一级"))
        self.UpLoad.setText(_translate("Form", "上传"))

