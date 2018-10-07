import cv2
import numpy as np
from utils import processing_utils as utils
from abc import ABCMeta, abstractmethod


class ImageProcessor:
    """ Abstract class for behavior based image processing.
    """
    __metaclass__ = ABCMeta

    def __init__(self, behavior):
        self._behavior = behavior
        self._unique_value = 0

    @abstractmethod
    def process_image(self, image_u, image_p):
        pass

    def behavior(self):
        return self._behavior

    def set_unique_value(self, value):
        self._unique_value = value


class FilterProcessor(ImageProcessor):
    def __init__(self, behavior):
        super(FilterProcessor, self).__init__(behavior)
        self._kernels = utils.Kernels().kernels_list

    def process_image(self, image_u, image_p):
        (_, k) = self._kernels[self._unique_value]
        return cv2.filter2D(image_p, -1, k)


class BrightnessProcessor(ImageProcessor):
    def __init__(self, behavior):
        super(BrightnessProcessor, self).__init__(behavior)

    def process_image(self, image_u, image_p):
        return cv2.addWeighted(image_u, 1.0, np.zeros(
                image_u.shape, dtype=image_u.dtype), 0, self._unique_value / 1.4)


class ContrastProcessor(ImageProcessor):
    def __init__(self, behavior):
        super(ContrastProcessor, self).__init__(behavior)

    def process_image(self, image_u, image_p):
        return cv2.addWeighted(image_p, 1.0 + self._unique_value / 127, np.zeros(
                image_u.shape, dtype=image_u.dtype), 0, 1.0)
