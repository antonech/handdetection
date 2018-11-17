import sys
import signal
from PyQt5.QtWidgets import QApplication
from hand_detection_main import HandDetectionMain

signal.signal(signal.SIGINT, signal.SIG_DFL)


def main():
    app = QApplication(sys.argv)
    handdetection = HandDetectionMain(app)
    try:
        handdetection.start()
        app.exec_()
    except KeyboardInterrupt:
        handdetection.join()


if __name__ == "__main__":
    main()

