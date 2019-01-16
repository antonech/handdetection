import cv2
import subprocess
import threading
import time
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QImage
from enum import Flag, auto
from hand_detection_window import CONFIG_FILE, HandDetectionWindow
from tensor_hand_detection import TensorflowDetector, output_q
from ini_config import IniConfig


class CommandTypes(Flag):
    NONE = 0
    COMMAND = auto()
    MOUSE = auto()
    CAPTURE_VIDEO = auto()


class HandDetectionMain(QObject):
    __lock = threading.RLock()

    def __init__(self, app):
        super(HandDetectionMain, self).__init__()

        self.config = IniConfig(CONFIG_FILE)

        self.uihand = HandDetectionWindow(app, stop_fn=self.stop, config=self.config)

        self.tensor = TensorflowDetector(standalone=False, score_thresh=0.88, src=self.config.get_video_src())
        self.executor = threading.Thread(name='executor', target=self.execute)

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
                img, boxes, scores, classes = output_q.get()
                for i, score in enumerate(scores):
                    if score > self.tensor.score_thresh:
                        acommand = classes[i]
                        box = boxes[i]
                        self.execute_command(acommand, box, img)

    def get_command(self, num):
        """
        Read command from ini config
        :param num: Combobox number 1,2,3,5 (Represents gesture index)
        :return:  Command
        """
        data = self.config.get_commands()
        combo_texts = self.config.get_combobox_texts()
        combo_commands = self.config.get_combobox()
        gui = self.config.get_gui()

        mouse_control = CommandTypes.MOUSE if gui.get('mouse_control', 'False') == 'True' else CommandTypes.NONE
        capture_video = CommandTypes.CAPTURE_VIDEO if gui.get('capture_stream', 'False') == 'True' \
            else CommandTypes.NONE
        if mouse_control & CommandTypes.MOUSE:
            return '', mouse_control | capture_video

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

        return command, CommandTypes.COMMAND | capture_video

    def execute_command(self, num, box, img):
        """
        Executes command after prediction
        :param num: Command number
        :param box: Border of the predicted figure
        :param img: Image to show
        :return:
        """

        data = self.inteval_commands_executor.get(num, {})
        start = data.get('time', 0)
        count = data.get('count', 0)
        end = time.monotonic()

        command, command_type = self.get_command(num)
        # Wait 0.5 sec between executions
        if start + 0.5 > end and count < 5 and not command_type & CommandTypes.MOUSE:
            count += 1
            self.inteval_commands_executor[num] = {
               'time': start,
               'count': count
            }
            return

        if command_type & CommandTypes.CAPTURE_VIDEO:
            self.plot(img, box)

        with self.__lock:

            if not command_type & CommandTypes.MOUSE:

                self.inteval_commands_executor[num] = {
                    'time': time.monotonic(),
                    'count': 0
                }

                try:
                    to_run = command.split(';')
                    for r in to_run:
                        subprocess.check_output(r.split())
                except FileNotFoundError:
                    print('Error')
            else:
                x_o, y_o = self.get_mouse_position()
                width = 1920
                height = 1080
                x = box[1] * width
                y = box[0] * height

                if width/2 < x:
                    x_o += 5
                else:
                    x_o -= 5

                if height/2 < y:
                    y_o += 5
                else:
                    y_o -= 5

                self.move(x_o, y_o)

    def plot(self, img, box):
        height = img.shape[0]
        width = img.shape[1]

        (left, right, top, bottom) = (box[1] * width, box[3] * width,
                                      box[0] * height, box[2] * height)
        p1 = (int(left), int(top))
        p2 = (int(right), int(bottom))

        cv2.rectangle(img, p1, p2, (77, 255, 9), 3, 3)

        image = QImage(img, img.shape[1], img.shape[0], img.shape[1] * 3, QImage.Format_RGB888)
        self.uihand.tray_icon.show_image(image)

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


