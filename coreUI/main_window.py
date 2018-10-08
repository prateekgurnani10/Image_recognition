import cv2
import numpy as np
from coreUI import slider_widget as slider
from utils import processing_utils as utils
from core import image_processor as processor
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QDir, QPoint
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QPushButton, QDesktopWidget
from PyQt5.uic import loadUi


# UI form
MAIN_WINDOW_UI = 'coreUI/main_window.ui'

# String definitions
BEHAVIOR_FILTER = "Filter:"
BEHAVIOR_BRIGHTNESS = "Brightness:"
BEHAVIOR_CONTRAST = "Contrast:"


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi(MAIN_WINDOW_UI, self)

        # Center the window on launch
        self.center()
        # Webcam option bar / Enable sub-option
        self.menuBar().addMenu("&Webcam").addAction("&Enable")
        # Exit button which will be added to the top menu bar
        self.exit_button = QPushButton(" X ", self.menuBar())
        self.menuBar().setCornerWidget(self.exit_button, QtCore.Qt.TopRightCorner)

        self._old_pos = QPoint()            # QMainWindow old position (position tracking)
        self._cascades = utils.Cascades()   # Mapping of cascades to their cascade classifiers
        self._kernels = utils.Kernels()     # Kernels for image filtering
        self._color_img = None              # Colored image
        self._grayscale_img = None          # Grayscale image
        self._processed_img = None          # Processed image
        self._rotated_img = None            # Rotated image

        # Initially create a filter processing behavior, passing it the list of kernel names
        fp_behavior = utils.ProcessingBehavior((
            0, len(self._kernels.kernels_list) - 1), BEHAVIOR_FILTER, 0)
        fp_behavior.setting_info = [k_n for (k_n, _) in self._kernels.kernels_list]

        # Maps behaviors to their respective ImageProcessor
        self._processors = {
            BEHAVIOR_BRIGHTNESS: processor.BrightnessProcessor(utils.ProcessingBehavior(
                (-50, 50), BEHAVIOR_BRIGHTNESS, 0)),
            BEHAVIOR_CONTRAST: processor.ContrastProcessor(utils.ProcessingBehavior(
                (-50, 50), BEHAVIOR_CONTRAST, 0)),
            BEHAVIOR_FILTER: processor.FilterProcessor(fp_behavior)
        }

        self.create_sliders()

        self.exit_button.clicked.connect(self.on_exit_button_clicked)
        self.importButton.clicked.connect(self.on_import_clicked)
        self.saveButton.clicked.connect(self.on_save_clicked)
        self.detectButton.clicked.connect(self.on_detect_clicked)

        # Image rotation connection loops
        # SpinBox and the dial are connected to each other's setters, along with each being able to
        # call rotate_image simultaneously
        self.rotateImgDial.valueChanged.connect(self.rotate_image)
        self.rotateImgSpinBox.valueChanged.connect(self.rotate_image)
        self.rotateImgDial.valueChanged.connect(self.rotateImgSpinBox.setValue)
        self.rotateImgSpinBox.valueChanged.connect(self.rotateImgDial.setValue)

    # Create a slider, passing the processor's behavior to the slider
    # Connect each widget to an on_slider_move slot which will catch an emitted slider behavior model
    def create_sliders(self):
        for key, value in self._processors.items():
            widget = slider.SliderWidget(value.behavior())
            widget.slider_moved.connect(self.on_slider_move)
            self.sliderLayout.addWidget(widget)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # Override
    def mousePressEvent(self, event):
        self._old_pos = event.globalPos()

    # Override
    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self._old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self._old_pos = event.globalPos()

    # Called when a signal from the slider widget is emitted
    def on_slider_move(self, behavior_name, slider_value):
        if self._color_img is None:
            return
        # Cache the processors unique value from it's respective slider position
        self._processors[behavior_name].set_unique_value(slider_value)

        # We need to loop through every processor and reprocess each time any slider is moved
        for (_, p) in self._processors.items():
            # Use the rotated image for any changed dimensions
            self._processed_img = p.process_image(self._rotated_img, self._processed_img)

        self.display_img(self._processed_img, self.rightImgLabel)

    @pyqtSlot()
    def rotate_image(self):
        if self._color_img is None:
            return

        angle = self.rotateImgDial.value()
        scale = 1.0

        w = self._color_img.shape[1]
        h = self._color_img.shape[0]
        r_angle = np.deg2rad(int(angle))  # Get the angle in radians

        # Calculate new image width and height
        nw = (abs(np.sin(r_angle) * h) + abs(np.cos(r_angle) * w)) * scale
        nh = (abs(np.cos(r_angle) * h) + abs(np.sin(r_angle) * w)) * scale

        # Get rotation matrix from openCV
        rotation_mat = cv2.getRotationMatrix2D((nw * 0.5, nh * 0.5), angle, scale)

        # Calculate the move from the old center to the new center combined w/ the rotation
        # (dot prod of the rotation matrix and the new matrix)
        rotation_move = np.dot(
            rotation_mat,
            np.array([(nw - w) * 0.5, (nh - h) * 0.5, 0])
        )

        # The move only affects the translation, so update the translation part of the transform
        rotation_mat[0, 2] += rotation_move[0]
        rotation_mat[1, 2] += rotation_move[1]

        # The rotated image will never include processing, it will only be used for the dimensions
        # We will always use the color image (original) for the base transformation calculations
        self._rotated_img = cv2.warpAffine(self._color_img, rotation_mat, (int(np.ceil(nw)), int(np.ceil(nh))))

        # Do processing every time the image is rotated, this time used the processed image in place of the
        # un-modified image. We want to use the size/shape of the transformed image this time
        for (_, p) in self._processors.items():
            self._processed_img = p.process_image(self._rotated_img, self._processed_img)

        self.display_img(self._processed_img, self.rightImgLabel)

    @pyqtSlot()
    def on_detect_clicked(self):
        if self._grayscale_img is None:
            return

        # Detect faces
        faces = self._cascades.cascades_list[utils.Cascades.CascadeList.FACE_CASCADE].detectMultiScale(
            self._grayscale_img, 1.3, 5)

        for (x, y, w, h) in faces:
            if self.detectFaceCheckBox.isChecked():
                cv2.rectangle(self._processed_img, (x, y), (x + w, y + h), (255, 0, 0), 3)
            else:
                self._processed_img = self._color_img.copy()

            roi_grayscale = self._grayscale_img[y: y + h, x: x + w]
            roi_color = self._color_img[y: y + h, x: x + w]

            if self.detectEyesCheckBox.isChecked():
                # Detect eyes
                eyes = self._cascades.cascades_list[utils.Cascades.CascadeList.EYE_CASCADE].detectMultiScale(
                    roi_grayscale, 1.1, 22)

                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
            else:
                self._processed_img[y: y + h, x: x + w] = self._color_img[y: y + h, x: x + w].copy()

            if self.detectSmileCheckBox.isChecked():
                # Detect smiles
                smile = self._cascades.cascades_list[utils.Cascades.CascadeList.SMILE_CASCADE].detectMultiScale(
                    roi_grayscale, 1.7, 18)

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
        self._rotated_img = self._color_img.copy()

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
