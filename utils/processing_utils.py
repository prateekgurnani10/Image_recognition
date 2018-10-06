import cv2
import numpy as np
from enum import Enum

# Image processing utility objects
#################################################################


class ProcessingBehavior:
    def __init__(self, min_max, name, default):
        self.min_max = min_max
        self.name = name
        self.default = default


class Cascades:

    class CascadeList(Enum):
        EYE_CASCADE = 0
        FACE_CASCADE = 1
        SMILE_CASCADE = 2

    def __init__(self):
        self.cascades_list = {
            self.CascadeList.EYE_CASCADE: cv2.CascadeClassifier("cascades/haarcascade_eye.xml"),
            self.CascadeList.FACE_CASCADE: cv2.CascadeClassifier("cascades/haarcascade_frontalface.xml"),
            self.CascadeList.SMILE_CASCADE: cv2.CascadeClassifier("cascades/haarcascade_smile.xml")
        }


class Kernels:

    class KernelList(Enum):
        IDENTITY_KERNEL = 0
        SHARPENING_KERNEL = 1
        GAUSSIAN_KERNEL_WEAK = 2
        GAUSSIAN_KERNEL_STRONG = 3
        BOX_KERNEL = 4

    def __init__(self):
        self.kernels_list = {
            # Any filtering position 0 should use the identity as default
            self.KernelList.IDENTITY_KERNEL: np.array([
                [0, 0, 0],
                [0, 1, 0],
                [0, 0, 0]
            ]),

            self.KernelList.SHARPENING_KERNEL: np.array([
                [0, -1,  0],
                [-1, 5, -1],
                [0, -1,  0]
            ]),

            self.KernelList.GAUSSIAN_KERNEL_WEAK: np.array([
                [1, 2, 1],
                [2, 4, 2],
                [1, 2, 1]
            ], np.float32) / 16,

            # Up (x,_) for a more blurry effect or to add more noise to the image
            self.KernelList.GAUSSIAN_KERNEL_STRONG: cv2.getGaussianKernel(8, 0),

            self.KernelList.BOX_KERNEL: np.array([
                [1, 1, 1],
                [1, 1, 1],
                [1, 1, 1]
            ], np.float32) / 9  # Normalize the matrix by dividing by the number of total entries
        }
