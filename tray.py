# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './form/tray.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_HandDetection(object):
    def setupUi(self, HandDetection):
        HandDetection.setObjectName("HandDetection")
        HandDetection.resize(480, 320)
        self.command1 = QtWidgets.QLineEdit(HandDetection)
        self.command1.setGeometry(QtCore.QRect(60, 54, 170, 25))
        self.command1.setObjectName("command1")
        self.command2 = QtWidgets.QLineEdit(HandDetection)
        self.command2.setGeometry(QtCore.QRect(300, 54, 170, 25))
        self.command2.setObjectName("command2")
        self.command3 = QtWidgets.QLineEdit(HandDetection)
        self.command3.setGeometry(QtCore.QRect(60, 109, 170, 25))
        self.command3.setObjectName("command3")
        self.img1 = QtWidgets.QLabel(HandDetection)
        self.img1.setGeometry(QtCore.QRect(-10, 27, 81, 51))
        self.img1.setStyleSheet("image: url(:/icons/image1.jpg);")
        self.img1.setText("")
        self.img1.setObjectName("img1")
        self.img1_2 = QtWidgets.QLabel(HandDetection)
        self.img1_2.setGeometry(QtCore.QRect(230, 27, 81, 51))
        self.img1_2.setStyleSheet("image: url(:/icons/image2.jpg)")
        self.img1_2.setText("")
        self.img1_2.setObjectName("img1_2")
        self.img1_3 = QtWidgets.QLabel(HandDetection)
        self.img1_3.setGeometry(QtCore.QRect(-10, 84, 81, 50))
        self.img1_3.setStyleSheet("image: url(:/icons/image3.jpg);")
        self.img1_3.setText("")
        self.img1_3.setObjectName("img1_3")
        self.img1_4 = QtWidgets.QLabel(HandDetection)
        self.img1_4.setGeometry(QtCore.QRect(230, 84, 81, 50))
        self.img1_4.setStyleSheet("image: url(:/icons/image5.jpg);")
        self.img1_4.setText("")
        self.img1_4.setObjectName("img1_4")
        self.command5 = QtWidgets.QLineEdit(HandDetection)
        self.command5.setGeometry(QtCore.QRect(300, 110, 170, 25))
        self.command5.setObjectName("command5")
        self.config = QtWidgets.QGroupBox(HandDetection)
        self.config.setGeometry(QtCore.QRect(10, 180, 461, 121))
        self.config.setObjectName("config")
        self.minimize = QtWidgets.QCheckBox(self.config)
        self.minimize.setGeometry(QtCore.QRect(10, 30, 141, 23))
        self.minimize.setObjectName("minimize")
        self.mouse = QtWidgets.QCheckBox(self.config)
        self.mouse.setGeometry(QtCore.QRect(10, 90, 130, 23))
        self.mouse.setObjectName("mouse")
        self.video = QtWidgets.QCheckBox(self.config)
        self.video.setGeometry(QtCore.QRect(10, 60, 130, 23))
        self.video.setObjectName("video")
        self.save_button = QtWidgets.QPushButton(self.config)
        self.save_button.setGeometry(QtCore.QRect(360, 90, 89, 20))
        self.save_button.setObjectName("save_button")
        self.cmmandlabel1 = QtWidgets.QLabel(HandDetection)
        self.cmmandlabel1.setGeometry(QtCore.QRect(60, 30, 81, 17))
        self.cmmandlabel1.setObjectName("cmmandlabel1")
        self.cmmandlabel1_2 = QtWidgets.QLabel(HandDetection)
        self.cmmandlabel1_2.setGeometry(QtCore.QRect(60, 90, 81, 17))
        self.cmmandlabel1_2.setObjectName("cmmandlabel1_2")
        self.cmmandlabel1_3 = QtWidgets.QLabel(HandDetection)
        self.cmmandlabel1_3.setGeometry(QtCore.QRect(300, 30, 81, 17))
        self.cmmandlabel1_3.setObjectName("cmmandlabel1_3")
        self.cmmandlabel1_4 = QtWidgets.QLabel(HandDetection)
        self.cmmandlabel1_4.setGeometry(QtCore.QRect(300, 90, 81, 17))
        self.cmmandlabel1_4.setObjectName("cmmandlabel1_4")

        self.retranslateUi(HandDetection)
        QtCore.QMetaObject.connectSlotsByName(HandDetection)

    def retranslateUi(self, HandDetection):
        _translate = QtCore.QCoreApplication.translate
        HandDetection.setWindowTitle(_translate("HandDetection", "Hand Detection - Gesture Control"))
        self.config.setTitle(_translate("HandDetection", "Configuration"))
        self.minimize.setText(_translate("HandDetection", "Minimize to tray"))
        self.mouse.setText(_translate("HandDetection", "Control mouse"))
        self.video.setText(_translate("HandDetection", "Capture stream"))
        self.save_button.setText(_translate("HandDetection", "Save"))
        self.cmmandlabel1.setText(_translate("HandDetection", "Command:"))
        self.cmmandlabel1_2.setText(_translate("HandDetection", "Command:"))
        self.cmmandlabel1_3.setText(_translate("HandDetection", "Command:"))
        self.cmmandlabel1_4.setText(_translate("HandDetection", "Command:"))

import images_rc
