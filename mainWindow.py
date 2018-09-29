import sys
from enum import Enum
import cv2
import qdarkstyle
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QDir, QFile, QTextStream, pyqtSignal
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

MAIN_WINDOW_DIALOG = 'main_window_dialog.ui'


class CascadeList(Enum):
    EYE_CASCADE = 0
    FACE_CASCADE = 1
    SMILE_CASCADE = 2


class Cascades:
    def __init__(self):
        self.cascades_list = {
            CascadeList.EYE_CASCADE: cv2.CascadeClassifier("cascades/haarcascade_eye.xml"),
            CascadeList.FACE_CASCADE: cv2.CascadeClassifier("cascades/haarcascade_frontalface.xml"),
            CascadeList.SMILE_CASCADE: cv2.CascadeClassifier("cascades/haarcascade_smile.xml")
        }


class MainWindow(QDialog):

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi(MAIN_WINDOW_DIALOG, self)

        self._cascades = Cascades()     # Mapping of cascades to their cascade classifiers
        self._color_img = None          # Colored image
        self._grayscale_img = None      # Grayscale image
        self._processed_img = None      # Processed image

        self.exitButton.clicked.connect(self.on_exit_button_clicked)
        self.importButton.clicked.connect(self.on_import_clicked)
        self.saveButton.clicked.connect(self.on_save_clicked)
        self.detectButton.clicked.connect(self.on_detect_clicked)
        self.cannySlider.valueChanged.connect(self.on_canny_slider_value_changed)

    @pyqtSlot()
    def on_canny_slider_value_changed(self):
        # Always set slider text
        self.cannySliderPositionLabel.setText(str(self.cannySlider.value()))
        if self._grayscale_img is None:
            return

        # Use the slider to determine canny image values
        canny_image = cv2.Canny(self._grayscale_img, self.cannySlider.value(), self.cannySlider.value() * 3)
        self.display_img(canny_image, self.rightImgLabel)

    @pyqtSlot()
    def on_detect_clicked(self):
        if self._grayscale_img is None:
            return

        # Detect faces
        faces = self._cascades.cascades_list[CascadeList.FACE_CASCADE].detectMultiScale(self._grayscale_img, 1.3, 5)
        for (x, y, w, h) in faces:
            if self.detectFaceCheckBox.isChecked():
                cv2.rectangle(self._processed_img, (x, y), (x + w, y + h), (255, 0, 0), 3)
            else:
                self._processed_img = self._color_img.copy()

            roi_grayscale = self._grayscale_img[y: y + h, x: x + h]
            roi_color = self._processed_img[y: y + h, x: x + h]

            if self.detectEyesCheckBox.isChecked():
                # Detect eyes
                eyes = self._cascades.cascades_list[CascadeList.EYE_CASCADE].detectMultiScale(roi_grayscale, 1.1, 22)
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
            else:
                self._processed_img[y: y + h, x: x + w] = self._color_img[y: y + h, x: x + w].copy()

            if self.detectSmileCheckBox.isChecked():
                smile = self._cascades.cascades_list[CascadeList.SMILE_CASCADE].detectMultiScale(roi_grayscale, 1.7, 18)
                for (sx, sy, sw, sh) in smile:
                    cv2.rectangle(roi_color, (sx, sy), (sx + sw, sy + sh), (0, 0, 255), 2)
            else:
                self._processed_img[y: y + h, x: x + w] = self._color_img[y: y + h, x: x + w].copy()

        self.display_img(self._processed_img, self.rightImgLabel)

    @pyqtSlot()
    def on_import_clicked(self):
        (filename, _) = QFileDialog.getOpenFileName(self, 'Open File', QDir.home().path(), "Image Files (*.jpg)")
        if filename:
            self.load_image(filename)

    @pyqtSlot()
    def on_save_clicked(self):
        (filename, _) = QFileDialog.getSaveFileName(self, 'Save File', QDir.home().path(), "Image Files (*.jpg)")
        if filename:
            cv2.imwrite(filename, self._processed_img)

    @pyqtSlot()
    def on_exit_button_clicked(self):
        self.close()

    def load_image(self, img_name):
        self._color_img = cv2.imread(img_name)
        self._grayscale_img = cv2.cvtColor(self._color_img, cv2.COLOR_BGR2GRAY)
        self._processed_img = self._color_img.copy()

        if self._color_img is None:
            print(f"Invalid image path: {img_name}")
        else:
            # Display the color image on the left panel first
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


####################################################################
def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
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
