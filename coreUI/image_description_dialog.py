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

        description_labels = [
            self.shapeDataLabel,
            self.channelsDataLabel,
            self.sizeDataLabel,
            self.datatypeDataLabel
        ]

        # Set up initial display labels
        utils.display_img(image, self.imageViewLabel)
        (h, w, c) = image.shape
        self.shapeDataLabel.setText(f"{w} x {h} pixels")
        self.channelsDataLabel.setText(f"{c}")
        self.sizeDataLabel.setText(f"{image.size} pixels")
        self.datatypeDataLabel.setText(f"{image.dtype}")

        # Resize all labels to match the max width
        max_label_width = 0
        for label in description_labels:
            if label.width() > max_label_width:
                max_label_width = label.width()

        for label in description_labels:
            # Add padding to the width for size dimensions
            label.setFixedWidth(max_label_width + 50)

        # CV image that is passed to the dialog menu
        # Note: We do not want a dialog without an image to accompany it
        self._image = image
        # Cache both the original and processed image
        self._processed_image = image.copy()

        self.applyButton.connect(self.on_apply_clicked)
        self.resetButton.connect(self.on_reset_clicked)

    def on_apply_clicked(self):
        """
        Handle when apply button is clicked
        :return:
        """
        pass

    def on_reset_clicked(self):
        """
        Handle when the reset button is clicked
        :return:
        """
        pass
