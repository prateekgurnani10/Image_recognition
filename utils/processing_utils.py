import cv2
import numpy as np
from enum import Enum


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

            ("Weak Gaussian", np.array([
                [1, 2, 1],
                [2, 4, 2],
                [1, 2, 1]
            ], np.float32) / 16),

            # Up (x,_) for a more blurry effect or to add more noise to the image
            ("Strong Gaussian 1", cv2.getGaussianKernel(8, 0)),

            ("Strong Gaussian 2", np.array([
                [1, 1, 1],
                [1, 1, 1],
                [1, 1, 1]
            ], np.float32) / 9)  # Normalize the matrix by dividing by the number of total entries
        ]
