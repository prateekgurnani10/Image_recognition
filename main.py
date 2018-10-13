# Python version 3.6

import os
import sys
import qdarkstyle
from coreUI import main_window as dejavu_window_main
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon


os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook


def my_exception_hook(exctype, value, traceback):
    """
    Helper function to help handle exceptions thrown by the event loop
    :param exctype: Exception type
    :param value: Call value
    :param traceback: Traceback error
    :return:
    """
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook


def main():
    """
    Application entry:
     * Sets up the QApplication
     * Creates the main window
     * Starts the event loop
    :return:
    """
    app = QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    app.setWindowIcon(QIcon('coreUI/dejavu_ir_logo_small.png'))

    window = dejavu_window_main.MainWindow()
    window.setWindowTitle("Dejavu Image Processing")
    window.show()

    try:
        sys.exit(app.exec_())
    except SystemError:
        print("Error")


if __name__ == '__main__':
    main()
