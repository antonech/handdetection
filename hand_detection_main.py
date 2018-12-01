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

        app.aboutToQuit.connect(self.stop)

        self.inteval_commands_executor = dict()

        self.started = False


    def execute(self):
        """
        Thread executor of predicted command
        :return:
        """
        while self.started:
            if output_q.qsize():
                _, boxes, scores, classes = output_q.get()
                for i, score in enumerate(scores):
                    if score > self.tensor.score_thresh:
                        acommand = classes[i]
                        box = boxes[i]
                        self.execute_command(acommand, box)

    def get_command(self, num):
        config = self.config.get()
        data = config.get('COMMANDS', {})
        combo_texts = config.get('COMBOBOX_TEXT', {})
        combo_commands = config.get('COMBOBOX', {})

        mouse_control = config.get('GUI', {}).get('mouse_control', False)

        if mouse_control != 'False':
            return 'mouse_control'

        acommands = {
                    1: data.get('command1'),
                    2: data.get('command2'),
                    3: data.get('command3'),
                    5: data.get('command4')
                }

        command = acommands.get(num)

        if command in combo_texts.values():
            idx = dict((v, k) for k, v in combo_texts.items())[command]
            command = combo_commands[idx]

        return command

    def execute_command(self, num, box):
        """
        Executes command after prediction
        :param num: Command number
        :param box: Border of the predicted figure
        :return:
        """

        start = self.inteval_commands_executor.get(num, 0)
        end = time.monotonic()

        command = self.get_command(num)
        # Wait 1 sec between executions
        if start + 1 > end and command != 'mouse_control':
            return

        with self.__lock:

            if command != 'mouse_control':

                self.inteval_commands_executor[num] = time.monotonic()

                if command:
                    try:
                        to_run = command.split(';')
                        for r in to_run:
                            subprocess.call(r.split())
                    except FileNotFoundError:
                        pass
            else:
                x_o, y_o = self.get_mouse_position()
                width = 1920
                height = 1080
                x = box[1] * width
                y = box[0] * height

                print(x, y)
                if width/2 < x:
                    x_o += 5
                else:
                    x_o -= 5

                if height/2 < y:
                    y_o += 5
                else:
                    y_o -= 5

                self.move(x_o, y_o)

    @staticmethod
    def get_mouse_position():
        from Xlib import display
        data = display.Display().screen().root.query_pointer()._data
        return data["root_x"], data["root_y"]

    @staticmethod
    def move(x, y):
        from Xlib.ext.xtest import fake_input
        from Xlib import display
        from Xlib import X
        d = display.Display()
        fake_input(d, X.MotionNotify, x=int(x), y=int(y))
        d.sync()

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

