import sys
import qdarkstyle
import main_window_dialog as dejavu_window_main
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

# Handle stupid Qt errors this way so they're not cryptic
#################################################################
# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook


####################################################################
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    window = dejavu_window_main.MainWindow()
    window.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    window.setWindowTitle("Dejavu Interface")
    window.show()

    try:
        sys.exit(app.exec_())
    except SystemError:
        print("Error")


####################################################################
if __name__ == '__main__':
    main()
