import cv2
import numpy as np
from utils import processing_utils as utils
from abc import ABCMeta, abstractmethod


class ImageProcessor:
    """Abstract class for behavior based image processing"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, behavior):
        """
        Constructor
        :param behavior: Image processing behavior
        :return:
        """
        self._behavior = behavior   # Processing behavior
        self._unique_value = 0      # Processors unique value

    @abstractmethod
    def process_image(self, image_u, image_p):
        """
        Do processing on an image
        :param image_u: Unchanged image (the original image)
        :param image_p: Processed image (image that has already had processing applied to it)
        :return: An image with additional processing done to it
        """
        pass

    def behavior(self):
        """
        Get the behavior of the processor
        :return: A Processing behavior
        """
        return self._behavior

    def set_unique_value(self, value):
        """
        Sets the processors unique value (which will be used for it's calculations ie: brightness/rotation angle
        :param value: The processors unique value
        :return:
        """
        self._unique_value = value


class FilterProcessor(ImageProcessor):
    """Filtering processor which applies kernel transformations to an image"""
    def __init__(self, behavior):
        super(FilterProcessor, self).__init__(behavior)
        self._kernels = utils.Kernels().kernels_list

    def process_image(self, image_u, image_p):
        (_, k) = self._kernels[self._unique_value]
        return cv2.filter2D(image_p, -1, k)


class BrightnessProcessor(ImageProcessor):
    """Brightness processor which will adjust brightness based on a given value"""
    def __init__(self, behavior):
        super(BrightnessProcessor, self).__init__(behavior)

    def process_image(self, image_u, image_p):
        return cv2.addWeighted(image_u, 1.0, np.zeros(
                image_u.shape, dtype=image_u.dtype), 0, self._unique_value / 1.4)


class ContrastProcessor(ImageProcessor):
    """Contrast processor which will adjust contrast based on a given value"""
    def __init__(self, behavior):
        super(ContrastProcessor, self).__init__(behavior)

    def process_image(self, image_u, image_p):
        return cv2.addWeighted(image_p, 1.0 + self._unique_value / 127, np.zeros(
                image_u.shape, dtype=image_u.dtype), 0, 1.0)


class RotationProcessor(ImageProcessor):
    """Rotation processor which apply matrix transformations to an original image based on a given angle"""
    def __init__(self, behavior):
        super(RotationProcessor, self).__init__(behavior)

    def process_image(self, image_u, image_p):
        angle = self._unique_value
        scale = 1.0

        w = image_u.shape[1]
        h = image_u.shape[0]
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
        return cv2.warpAffine(image_u, rotation_mat, (int(np.ceil(nw)), int(np.ceil(nh))))
