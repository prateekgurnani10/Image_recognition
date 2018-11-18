import cv2
import numpy as np
from utils import processing_utils as utils
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

IMAGE_DESCRIPT_DIALOG_UI = 'coreUI/image_description_dialog.ui'


class ImageDescriptionDialog(QDialog):
    """Image Description Dialog Window"""

    def __init__(self, image):
        super(ImageDescriptionDialog, self).__init__()
        loadUi(IMAGE_DESCRIPT_DIALOG_UI, self)

        # Set up initial display labels
        utils.display_img(image, self.imageViewLabel)
        (h, w, c) = image.shape
        self.shapeLabel.setText(
            f"Width: {w} pixels \nHeight: {h} pixels")

        self.colorLabel.setText(f"Image channels: {c}")
        self.sizeLabel.setText(f"Size: {image.size} pixels")

        # CV image that is passed to the dialog menu
        # Note: We do not want a dialog without an image to accompany it
        self._image = image
        # Cache both the original and processed image
        self._processed_image = image.copy()
