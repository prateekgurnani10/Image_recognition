import cv2
import numpy as np
from enum import Enum

from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap


class ProcessingBehavior:
    """Image processing behavior"""

    def __init__(self, min_max, name, default):
        self.min_max = min_max  # Behavior min and max processing ranges
        self.name = name        # Behavior name
        self.default = default  # Behavior default processing value
        self.setting_info = []  # Behavior setting information for each value b/t min-max


class Cascades:
    """Cascade helper which contains an easy way to import and store cascades"""

    class CascadeList(Enum):
        """Cascade list enum class"""
        EYE_CASCADE = 0
        FACE_CASCADE = 1

    def __init__(self):
        self.cascades_list = {
            self.CascadeList.EYE_CASCADE: cv2.CascadeClassifier("cascades/haarcascade_eye.xml"),
            self.CascadeList.FACE_CASCADE: cv2.CascadeClassifier("cascades/haarcascade_frontalface.xml")
        }


class Kernels:
    """Kernel helper which contains a container of kernels"""

    def __init__(self):
        # 2-tuples which contain (kernel string name, kernel matrix)
        self.kernels_list = [
            # Any filtering position 0 should use the identity as default
            ("Identity", np.array([
                [0, 0, 0],
                [0, 1, 0],
                [0, 0, 0]
            ])),

            ("Sharpening", np.array([
                [0, -1,  0],
                [-1, 5, -1],
                [0, -1,  0]
            ])),

            ("Blurring", np.array([
                [1, 1, 1],
                [1, 1, 1],
                [1, 1, 1]
            ], np.float32) / 9),  # Normalize the matrix by dividing by the number of total entries

            ("Blurring", np.array([
                [1, 2, 1],
                [2, 4, 2],
                [1, 2, 1]
            ], np.float32) / 16),

            # Up (x,_) for a more blurry effect or to add more noise to the image
            ("Blurring", cv2.getGaussianKernel(8, 0)),

            ("Edge Detection", np.array([
                [1,  0, -1],
                [0,  0,  0],
                [-1, 0,  1]
            ])),

            ("Edge Detection", np.array([
                [0,  1,  0],
                [1, -4,  1],
                [0,  1,  0]
            ])),

            ("Edge Detection", np.array([
                [-1, -1, -1],
                [-1,  8, -1],
                [-1, -1, -1]
            ]))
        ]


def display_img(image, image_label, scale_contents=False):
    """
    Display an image on a given image label
    :param image: The image to display (from openCV)
    :param image_label: The QLabel to display the image on
    :param scale_contents: Scale the contents to the label
    :return:
    """
    # Ensure the proper image format before storing as a QImage
    q_format = QImage.Format_Indexed8

    if len(image.shape) == 3:  # rows[0], cols[1], channels[2]
        if image.shape[2] == 4:
            q_format = QImage.Format_RGBA8888
        else:
            q_format = QImage.Format_RGB888

    (h, w) = image.shape[:2]
    q_image = QImage(image, w, h, image.strides[0], q_format)
    q_image = q_image.scaled(500, 500, QtCore.Qt.KeepAspectRatio)

    # Since openCV loads an image as BGR, we need to convert from BGR -> RBG
    img = q_image.rgbSwapped()

    # Resize the label to the scaled images width and height
    image_label.resize(img.rect().width(), img.rect().height())
    image_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
    # Set the image -> pixmap -> label
    image_label.setPixmap(QPixmap.fromImage(img))
    image_label.setScaledContents(scale_contents)
