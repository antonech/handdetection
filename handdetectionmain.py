import threading
import signal

from handdetection import  TensorflowDetector, output_q
from PyQt5.QtWidgets import QMainWindow, QSystemTrayIcon, QStyle, QAction, QMenu
from tray import Ui_HandDetection



class HandDetectionMain(object):

    def __init__(self, app):
        super(HandDetectionMain, self).__init__()

        self.tensor = TensorflowDetector(standalone=False)
        self.executor = threading.Thread(name='executor', target=self.execute)
        self.started = False
        self.stopped = False
        self.app = app

        mw = QMainWindow()
        icon = mw.style().standardIcon(QStyle.SP_ComputerIcon)
        mw.setWindowIcon(icon)
        mw.closeEvent = self.close_event

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
        self.tray_icon = tray_icon

        uihand = Ui_HandDetection()
        uihand.setupUi(mw)

        self.uihand = uihand
        self.mw = mw

    def show(self):
        self.tray_icon.show()
        self.mw.show()

    def hide(self):
        self.mw.hide()

    # Override closeEvent, to intercept the window closing event
    # The window will be closed only if there is no check mark in the check box
    def close_event(self, event):
        if self.uihand.minimize.isChecked():
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

