import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QSystemTrayIcon, QStyle, QAction, QMenu
from tray import Ui_HandDetection


def main():
    app = QApplication(sys.argv)
    mw = QMainWindow()

    icon = mw.style().standardIcon(QStyle.SP_ComputerIcon)
    mw.setWindowIcon(icon)

    # Init QSystemTrayIcon
    tray_icon = QSystemTrayIcon(mw)
    tray_icon.setIcon(icon)

    '''
       Define and add steps to work with the system tray icon
       show - show window
       hide - hide window
       exit - exit from application
   '''
    show_action = QAction("Show", mw)
    quit_action = QAction("Exit", mw)
    hide_action = QAction("Hide", mw)
    show_action.triggered.connect(mw.show)
    hide_action.triggered.connect(mw.hide)
    quit_action.triggered.connect(app.quit)

    tray_menu = QMenu()
    tray_menu.addAction(show_action)
    tray_menu.addAction(hide_action)
    tray_menu.addAction(quit_action)
    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()

    uihand = Ui_HandDetection()
    uihand.setupUi(mw)

    mw.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

