import sys
import cv2
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.uic import loadUi
from qtpy import QtCore

DIALOG_NAME = 'main_dialog.ui'


class MainWindow(QDialog):

    _img = None

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi(DIALOG_NAME, self)

        self.importButton.clicked.connect(self.on_import_clicked)

    @pyqtSlot()
    def on_import_clicked(self):
        self.load_image('scene10.png')

    def load_image(self, img_name):
        self._img = cv2.imread(img_name)
        if self._img is None:
            print(f"Invalid image path: {img_name}")
        else:
            self.display_img()

    def display_img(self):
        # Ensure the proper image format before storing as a QImage
        q_format = QImage.Format_Indexed8

        if len(self._img.shape) == 3:  # rows[0], cols[1], channels[2]
            if self._img.shape[2] == 4:
                q_format = QImage.Format_RGBA8888
            else:
                q_format = QImage.Format_RGB888

        # Alternative way to export to pixmap
        # (height, width, channel) = self._img.shape
        # bytes_per_line = 3 * width
        # img_1 = QImage(self._img.data, width, height, bytes_per_line, q_format)

        img = QImage(self._img, self._img.shape[1], self._img.shape[0], self._img.strides[0], q_format)

        # Since openCV loads an image as BGR, we need to convert from BGR -> RBG
        img = img.rgbSwapped()
        self.imgLabel.setPixmap(QPixmap.fromImage(img))
        self.imgLabel.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Dejavu Interface")
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
