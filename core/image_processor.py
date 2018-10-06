import cv2
from utils import processing_utils as utils
from abc import ABCMeta, abstractmethod


class ImageProcessor:
    """ Abstract class for behavior based image processing.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def process_image(self, image, value):
        pass

    @abstractmethod
    def behavior(self):
        pass


# Kernel filtering
class FilterProcessor(ImageProcessor):
    def __init__(self, behavior):
        self._behavior = behavior                       # Processing behavior
        self._kernels = utils.Kernels().kernels_list    # Kernels

    def process_image(self, image, value):
        (_, k) = self._kernels[value]
        return cv2.filter2D(image, -1, k)

    def behavior(self):
        return self._behavior


class BrightnessProcessor(ImageProcessor):
    def __init__(self, behavior):
        self._behavior = behavior

    def process_image(self, image, value):
        return image

    def behavior(self):
        return self._behavior


class ContrastProcessor(ImageProcessor):
    def __init__(self, behavior):
        self._behavior = behavior

    def process_image(self, image, value):
        return image

    def behavior(self):
        return self._behavior
