import subprocess
import threading
import time
from PyQt5.QtCore import QObject

from hand_detection_window import CONFIG_FILE, HandDetectionWindow
from tensor_hand_detection import TensorflowDetector, output_q
from ini_config import IniConfig


class HandDetectionMain(QObject):
    __lock = threading.RLock()

    def __init__(self, app):
        super(HandDetectionMain, self).__init__()

        self.tensor = TensorflowDetector(standalone=False)
        self.executor = threading.Thread(name='executor', target=self.execute)

        self.config = IniConfig(CONFIG_FILE)
        self.uihand = HandDetectionWindow(app, stop_fn=self.stop, config=self.config)

        self.inteval_commands_executor = dict()

        self.started = False

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
                    to_run = command.split(';')
                    for r in to_run:
                        subprocess.call(r.split())
                except FileNotFoundError:
                    pass

    @staticmethod
    def get_mouse_position():
        from Xlib import display
        data = display.Display().screen().root.query_pointer()._data
        return data["root_x"], data["root_y"]

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
        self.stop()
        self.tensor.join()
        self.executor.join()

