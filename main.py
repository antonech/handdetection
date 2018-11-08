import sys
from PyQt5.QtWidgets import QApplication
from handdetectionmain import HandDetectionMain


def main():
    app = QApplication(sys.argv)

    handdetection = HandDetectionMain(app)
    handdetection.start()
    app.exec()


if __name__ == "__main__":
    main()

