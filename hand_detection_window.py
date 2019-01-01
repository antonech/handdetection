from distutils.util import strtobool

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QStyle, QSystemTrayIcon, QAction, QMenu, QDesktopWidget

from ini_config import IniConfig
from hand_detection_window_form import Ui_HandDetection
from tray_icon import SystemTrayIcon

CONFIG_FILE = 'detection.ini'


class HandDetectionWindow(QMainWindow, Ui_HandDetection):

    def __init__(self, app, **kwargs):
        super(HandDetectionWindow, self).__init__()
        self.setupUi(self)
        self.stop = kwargs.get('stop_fn', lambda: None)
        self.config = kwargs.get('config', IniConfig(CONFIG_FILE))
        icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.setWindowIcon(icon)

        # Init QSystemTrayIcon
        tray_icon = SystemTrayIcon(self)
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
            'capture_stream': self.video,
        }

        combobox_commands = data.get('COMBOBOX_TEXT', {})
        texts = data.get('COMBOBOX_TEXT', {})

        for c in acommand.values():
            for idx, txt in texts.items():
                c.addItem(txt, combobox_commands.get(idx, ''))

        commands = data.get("COMMANDS", {})

        for k, v in commands.items():
            command = acommand.get(k)
            if command is not None:
                command.setEditText(v)

        gui = data.get("GUI", {})

        for k, v in gui.items():
            gui_check_box = agui.get(k)
            if gui_check_box:
                gui_check_box.setChecked(strtobool(v))

        x = gui.get('position_x')
        y = gui.get('position_y')

        if x and x.isdigit() and y and y.isdigit():
            self.move(int(x), int(y))

        if not self.minimize.isChecked():
            self.show()

    @pyqtSlot()
    def save_config(self):
        size = self.geometry()

        data = {
            'COMMANDS': {
                'command1': self.command1.currentText(),
                'command2': self.command2.currentText(),
                'command3': self.command3.currentText(),
                'command4': self.command5.currentText()
            },
            'GUI': {
                'minimize': self.minimize.isChecked(),
                'mouse_control': self.mouse.isChecked(),
                'capture_stream': self.video.isChecked(),
                'position_x': size.left(),
                'position_y': size.top()
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
                "Hands Detection",
                "Application was minimized to Tray",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            self.stop()
