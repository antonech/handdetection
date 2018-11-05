import threading

from configparser import ConfigParser
from os.path import isfile

from PyQt5.QtCore import pyqtSlot, QObject

from handdetection import  TensorflowDetector, output_q
from PyQt5.QtWidgets import QMainWindow, QSystemTrayIcon, QStyle, QAction, QMenu, QWidget
from tray import Ui_HandDetection


class HandDetection(QMainWindow, Ui_HandDetection):

    CONFIG_FILE = 'detection.ini'

    def __init__(self, app):
        super(HandDetection, self).__init__()
        self.setupUi(self)

        icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.setWindowIcon(icon)

        # Init QSystemTrayIcon
        tray_icon = QSystemTrayIcon(self)
        tray_icon.setIcon(icon)

        '''
           Define and add steps to work with the system tray icon
           show - show window
           hide - hide window
           exit - exit from application
       '''
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(app.quit)

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        tray_icon.setContextMenu(tray_menu)
        self.tray_icon = tray_icon

        self.app = app
        self.save_button.clicked.connect(self.save_config)

        self.config = ConfigParser()

        self.init_config()

    def init_config(self):

        if isfile(self.CONFIG_FILE):
            with open(self.CONFIG_FILE) as cfg:
                self.config.read_file(cfg)

        if 'COMMANDS' in self.config.sections():
            commands = self.config['COMMANDS']
            command1 = commands.get('command1', '')
            command2 = commands.get('command2', '')
            command3 = commands.get('command3', '')
            command4 = commands.get('command4', '')

            self.command1.setText(command1)
            self.command2.setText(command2)
            self.command3.setText(command3)
            self.command5.setText(command4)

    @pyqtSlot()
    def save_config(self):
        self.config['COMMANDS'] = {
                'command1': self.command1.text(),
                'command2': self.command2.text(),
                'command3': self.command3.text(),
                'command4': self.command5.text()
            }

        with open(self.CONFIG_FILE, 'w') as cfg:
            self.config.write(cfg)

    def show(self):
        self.tray_icon.show()
        super().show()

    # Override closeEvent, to intercept the window closing event
    # The window will be closed only if there is no check mark in the check box
    def closeEevent(self, event):
        if self.minimize.isChecked():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Tray Program",
                "Application was minimized to Tray",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            self.stop()


class HandDetectionMain(QObject):

    def __init__(self, app):
        super(HandDetectionMain, self).__init__()

        self.tensor = TensorflowDetector(standalone=False)
        self.executor = threading.Thread(name='executor', target=self.execute)

        self.uihand = HandDetection(app)
        self.uihand.show()

        self.started = False

    def execute(self):
        while self.started:
            if output_q.qsize():
                _, boxes, scores, classes = output_q.get()
                for i, score in enumerate(scores):
                    if score > self.tensor.score_thresh:
                        print(score, classes[i])

    def start(self):
        if self.started:
            return

        self.started = True
        self.executor.daemon = True

        self.tensor.start()
        self.executor.start()

    def stop(self):

        if not self.started:
            return

        self.tensor.stop()
        self.started = False

        self.executor.join()

    def join(self):
        try:
            self.tensor.join()
            self.executor.join()
        except KeyboardInterrupt:
            self.stop()

