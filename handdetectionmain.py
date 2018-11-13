import subprocess
import threading
import time

from PyQt5.QtCore import pyqtSlot, QObject
from PyQt5.QtWidgets import QMainWindow, QSystemTrayIcon, QStyle, QAction, QMenu, QWidget
from distutils.util import strtobool
from handdetection import TensorflowDetector, output_q
from ini_config import IniConfig
from tray import Ui_HandDetection

CONFIG_FILE = 'detection.ini'


class HandDetection(QMainWindow, Ui_HandDetection):

    def __init__(self, app, **kwargs):
        super(HandDetection, self).__init__()
        self.setupUi(self)
        self.stop = kwargs.get('stop_fn', lambda: None)
        self.config = kwargs.get('config', IniConfig(CONFIG_FILE))
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

        self.init_config()

        # show icon no need to check the config
        self.tray_icon.show()

    def init_config(self):
        self.config.init_config()

        data = self.config.get()

        acommand = {
            'command1': self.command1,
            'command2': self.command2,
            'command3': self.command3,
            'command4': self.command5
        }

        agui = {
            'minimize': self.minimize,
            'mouse_control': self.mouse,
            'capture_stream': self.video
        }

        commands = data.get("COMMANDS", {})

        for k, v in commands.items():
            command = acommand.get(k)
            if command:
                command.setText(v)

        gui = data.get("GUI", {})

        for k, v in gui.items():
            gui_check_box = agui.get(k)
            if gui_check_box:
                gui_check_box.setChecked(strtobool(v))

    @pyqtSlot()
    def save_config(self):
        data = {
            'COMMANDS': {
                'command1': self.command1.text(),
                'command2': self.command2.text(),
                'command3': self.command3.text(),
                'command4': self.command5.text()
            },
            'GUI': {
                'minimize': self.minimize.isChecked(),
                'mouse_control': self.mouse.isChecked(),
                'capture_stream': self.video.isChecked()
            }
        }

        self.config.save_config(data)

    def show(self):
        super().show()

    # Override closeEvent, to intercept the window closing event
    # The window will be closed only if there is no check mark in the check box
    def closeEvent(self, event):
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
    __lock = threading.RLock()

    def __init__(self, app):
        super(HandDetectionMain, self).__init__()

        self.tensor = TensorflowDetector(standalone=False)
        self.executor = threading.Thread(name='executor', target=self.execute)

        self.config = IniConfig(CONFIG_FILE)
        self.uihand = HandDetection(app, stop_fn=self.stop, config=self.config)
        if not self.uihand.minimize.isChecked():
            self.uihand.show()

        self.started = False

        self.inteval_commands_executor = dict()

    def execute(self):

        while self.started:
            if output_q.qsize():
                _, boxes, scores, classes = output_q.get()
                for i, score in enumerate(scores):
                    if score > self.tensor.score_thresh:
                        acommand = classes[i]
                        print(score, classes[i])
                        self.execute_command(acommand)

    def execute_command(self, num):
        data = self.config.get().get('COMMANDS', {})

        start = self.inteval_commands_executor.get(num, 0)
        end = time.monotonic()

        print('in execute command', end - start)

        if start + 1 > end:
            return

        with self.__lock:
            print('execute command', end-start)
            acommands = {
                1: data.get('command1'),
                2: data.get('command2'),
                3: data.get('command3'),
                5: data.get('command4')
            }
            self.inteval_commands_executor[num] = time.monotonic()

            command = acommands.get(num)
            if command:
                try:
                    subprocess.call(command.split())
                except FileNotFoundError:
                    pass

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

