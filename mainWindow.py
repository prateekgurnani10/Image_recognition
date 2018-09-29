import sys

import cv2
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QDir
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.uic import loadUi

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

# TODO: Programmatically create behaviors such as contrast/brightness, when a behavior is added to the imageProcessor,
# TODO: create a slider for it, and connect the slider to the behavior
# TODO: image processor should contain an array or map of behaviors (can use an enum-like class to store strings)


DIALOG_NAME = 'main_dialog.ui'


class MainWindow(QDialog):

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi(DIALOG_NAME, self)

        self._color_img = None
        self._grayscale_img = None

        self.importButton.clicked.connect(self.on_import_clicked)
        self.saveButton.clicked.connect(self.on_save_clicked)
        self.cannyButton.clicked.connect(self.on_canny_clicked)
        self.cannySlider.valueChanged.connect(self.on_canny_slider_value_changed)

    @pyqtSlot()
    def on_canny_slider_value_changed(self):
        if self._grayscale_img is None:
            return

        # Use the slider to determine canny image values
        canny_image = cv2.Canny(self._grayscale_img, self.cannySlider.value(), self.cannySlider.value() * 3)
        self.display_img(canny_image, self.rightImgLabel)

    @pyqtSlot()
    def on_canny_clicked(self):
        if self._grayscale_img is None:
            return

        # Preset canny image filter on button click
        canny_image = cv2.Canny(self._grayscale_img, 100, 200)
        self.display_img(canny_image, self.rightImgLabel)

    @pyqtSlot()
    def on_import_clicked(self):
        (filename, _) = QFileDialog.getOpenFileName(self, 'Open File', QDir.home().path(), "Image Files (*.png)")
        if filename:
            self.load_image(filename)

    @pyqtSlot()
    def on_save_clicked(self):
        (filename, _) = QFileDialog.getSaveFileName(self, 'Save File', QDir.home().path(), "Image Files (*.png)")
        if filename:
            cv2.imwrite(filename, self._color_img)

    def load_image(self, img_name):
        self._color_img = cv2.imread(img_name)
        self._grayscale_img = cv2.cvtColor(self._color_img, cv2.COLOR_BGR2GRAY)

        if self._color_img is None:
            print(f"Invalid image path: {img_name}")
        else:
            self.display_img(self._color_img, self.leftImgLabel)

    @staticmethod
    def display_img(image, image_label):
        # Ensure the proper image format before storing as a QImage
        q_format = QImage.Format_Indexed8

        if len(image.shape) == 3:  # rows[0], cols[1], channels[2]
            if image.shape[2] == 4:
                q_format = QImage.Format_RGBA8888
            else:
                q_format = QImage.Format_RGB888

        q_image = QImage(image, image.shape[1], image.shape[0], image.strides[0], q_format)
        q_image = q_image.scaled(500, 500, QtCore.Qt.KeepAspectRatio)

        # Since openCV loads an image as BGR, we need to convert from BGR -> RBG
        img = q_image.rgbSwapped()
        image_label.setPixmap(QPixmap.fromImage(img))

        # Resize the label to the scaled images width and height
        image_label.resize(img.rect().width(), img.rect().height())
        image_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Dejavu Interface")
    window.show()

    try:
        sys.exit(app.exec_())
    except SystemError:
        print("Error")


if __name__ == '__main__':
    main()
