from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSystemTrayIcon, QLabel, QDesktopWidget, QWidget, QStyle


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        QSystemTrayIcon.__init__(self, parent)
        self.balloon = BalloonWidget("image")

    def show_image(self, img):
        self.balloon.show(img)


class BalloonWidget(QWidget):
    def __init__(self, name):
        QWidget.__init__(self, parent=None, flags=Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint)

        icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.setWindowIcon(icon)

        self.name = name

        self.outInfo = QLabel(self)

    def show(self, img):
        self.outInfo.setPixmap(QPixmap(img).scaled(256, 256, aspectRatioMode=Qt.KeepAspectRatio))
        self.outInfo.show()
        self.adjustSize()

        origin = QDesktopWidget().availableGeometry().topRight()
        move_x = origin.x()/2 - 128
        move_y = 50

        self.move(move_x, move_y)
        self.setVisible(True)

    def mousePressEvent(self, event):
        self.hide()
