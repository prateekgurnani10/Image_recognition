import cv2
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QRegion
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from utils import processing_utils as utils
from core import detector


IMAGE_DESCRIPT_DIALOG_UI = 'coreUI/webcam_dialog.ui'


class WebcamDialog(QDialog):
    """Webcam Dialog Window"""

    # Resized signal
    resized = pyqtSignal()

    def __init__(self):
        super(WebcamDialog, self).__init__()
        loadUi(IMAGE_DESCRIPT_DIALOG_UI, self)

        self.webcamDisplayLabel.setMouseTracking(False)
        self.mask_label_region()

        # Webcam capture
        self._capture = None
        # Image capture
        self._image = None
        # Detected image
        self._image_detected = None
        # Frame timers
        self._frame_timer = None
        # Is facial recognition active?
        self._recog_active = False
        # Image recognition detector object
        self._detector = detector.Detector()

        self.enableDisableRecogButton.clicked.connect(self.on_enable_disable_recog_clicked)
        self.startWebcamButton.clicked.connect(self.on_start_webcam_clicked)
        self.stopPauseWebcamButton.clicked.connect(self.on_stop_pause_webcam_clicked)

    def resizeEvent(self, event):
        """
        Override the resize event handle so that we can create our own resize signal
        :param event: Event
        :return: The new resize event
        """
        self.mask_label_region()
        self.resized.emit()
        return super(WebcamDialog, self).resizeEvent(event)

    def on_enable_disable_recog_clicked(self):
        """
        Handle when the enable/disable recognition button is clicked
        :return:
        """
        self._recog_active = not self._recog_active

    def on_start_webcam_clicked(self):
        """
        Handle when the start webcam button is clicked
        :return:
        """
        self._capture = cv2.VideoCapture(0)
        # Get initial label dimensions
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.webcamDisplayLabel.height())
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.webcamDisplayLabel.width())

        self._frame_timer = QTimer(self)
        self._frame_timer.timeout.connect(self.update_frame)
        self._frame_timer.start(5)

    def update_frame(self):
        """
        Handle when the frame timer times out
        :return:
        """
        (_, self._image) = self._capture.read()

        # Flip the image after reading
        self._image = cv2.flip(self._image, 1)
        self._image_detected = self._image.copy()

        if self._recog_active:
            grayscale_img = cv2.cvtColor(self._image, cv2.COLOR_BGR2GRAY)
            self._image_detected = self._detector.detect(grayscale_img, self._image)

        utils.display_img(self._image_detected, self.webcamDisplayLabel, scale_contents=True)
        self._image_detected = self._image.copy()

    def on_stop_pause_webcam_clicked(self):
        """
        Handle when the stop/pause webcam button is clicked
        :return:
        """
        self._frame_timer.stop()

    def mask_label_region(self):
        """
        Mask the webcam label region to avoid mouse events
        :return:
        """
        region = QRegion(self.webcamDisplayLabel.frameGeometry())
        region -= QRegion(self.webcamDisplayLabel.geometry())
        region += self.webcamDisplayLabel.childrenRegion()
        self.webcamDisplayLabel.setMask(region)