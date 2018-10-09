import cv2
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
BEHAVIOR_ROTATION = "Rotation"


class MainWindow(QMainWindow):
    """Main UI window"""

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

        # Rotation behavior will be used independent of the sliders, since rotation uses a QDial/QSpinBox
        rotation_behavior = utils.ProcessingBehavior(
            (self.rotateImgDial.minimum(), self.rotateImgDial.maximum()), BEHAVIOR_ROTATION, 0)
        self._rotation_processor = processor.RotationProcessor(rotation_behavior)

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

    def create_sliders(self):
        """
        Creates a slider for each processing behavior, and connects each of the sliders to a widget
        container. The widget will emit a signal every time it's slider is moved
        """
        for key, value in self._processors.items():
            widget = slider.SliderWidget(value.behavior())
            widget.slider_moved.connect(self.on_slider_move)
            self.sliderLayout.addWidget(widget)

    def center(self):
        """
        Move the UI location to the center of the screen
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # Override
    def mousePressEvent(self, event):
        """
        Catch when the mouse is pressed (this is used for moving the UI around)
        :param event: Mouse press event
        """
        self._old_pos = event.globalPos()

    # Override
    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self._old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self._old_pos = event.globalPos()

    def on_slider_move(self, behavior_name, slider_value):
        """
        Slot which catches emitted slider movements
        :param behavior_name: Processor behavior.name
        :param slider_value: QSlider value from the UI
        """
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
        """
       Handle when an image is rotated via the dial or spinbox
        """
        if self._color_img is None:
            return

        self._rotation_processor.set_unique_value(self.rotateImgDial.value())
        self._rotated_img = self._rotation_processor.process_image(self._color_img, self._processed_img)

        # Do processing every time the image is rotated, this time used the processed image in place of the
        # un-modified image. We want to use the size/shape of the transformed image this time
        for (_, p) in self._processors.items():
            self._processed_img = p.process_image(self._rotated_img, self._processed_img)

        self.display_img(self._processed_img, self.rightImgLabel)

    @pyqtSlot()
    def on_detect_clicked(self):
        """
        Handle when the detect button is clicked on the UI
        """
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
        """
        Handle when the import button is clicked on the UI
        """
        (filename, _) = QFileDialog.getOpenFileName(self, 'Open File', QDir.home().path(), "Image Files (*.jpg)")
        if filename:
            self.load_image(filename)

    @pyqtSlot()
    def on_save_clicked(self):
        """
        Handle when the save button is clicked on the UI
        """
        (filename, _) = QFileDialog.getSaveFileName(self, 'Save File', QDir.home().path(), "Image Files (*.jpg)")
        if filename:
            cv2.imwrite(filename, self._processed_img)

    @pyqtSlot()
    def on_exit_button_clicked(self):
        """
        Handle when the exit button is clicked on the UI
        """
        self.close()

    def load_image(self, img_path):
        """
        Loads an image
        :param img_path: The path to (including) the image
        :return: Return nothing if the image is not found
        """
        self._color_img = cv2.imread(img_path)
        self._grayscale_img = cv2.cvtColor(self._color_img, cv2.COLOR_BGR2GRAY)
        self._processed_img = self._color_img.copy()
        self._rotated_img = self._color_img.copy()

        if self._color_img is None:
            return
        else:
            # Display the color image on the left panel first
            self.display_img(self._color_img, self.leftImgLabel)

    @staticmethod
    def display_img(image, image_label):
        """
        Display an image on a given image label
        :param image: The image to display (from openCV)
        :param image_label: The QLabel to display the image on
        """
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
