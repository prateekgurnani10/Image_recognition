import sys
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.uic import loadUi

DIALOG_NAME = 'main_dialog.ui'


class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi(DIALOG_NAME, self)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Dejavu Interface")
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
