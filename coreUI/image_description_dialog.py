import cv2
import numpy as np
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from utils import processing_utils as utils

IMAGE_DESCRIPT_DIALOG_UI = 'coreUI/image_description_dialog.ui'


class ImageDescriptionDialog(QDialog):
    """Image Description Dialog Window"""

    def __init__(self, image):
        super(ImageDescriptionDialog, self).__init__()
        loadUi(IMAGE_DESCRIPT_DIALOG_UI, self)

        self.kernel_matrix_edits = [
            self.m_r1c1,
            self.m_r2c1,
            self.m_r3c1,
            self.m_r1c2,
            self.m_r2c2,
            self.m_r3c2,
            self.m_r1c3,
            self.m_r2c3,
            self.m_r3c3,
        ]
        self.set_validation()

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

        self.applyButton.clicked.connect(self.on_apply_clicked)
        self.resetButton.clicked.connect(self.on_reset_clicked)

    def on_apply_clicked(self):
        """
        Handle when apply button is clicked
        Only apply the matrix when it meets all validation criteria
        :return:
        """
        if self.verify_not_empty():
            print("no fields missing")
            pass
        else:
            print("one or more fields are missing")

    def on_reset_clicked(self):
        """
        Handle when the reset button is clicked
        :return:
        """
        pass

    def verify_not_empty(self):
        """
        Verify that all text fields are not empty
        :return: True only if all fields are not empty
        """
        for text_edit in self.kernel_matrix_edits:
            if not text_edit.hasAcceptableInput():
                return False

        return True

    def set_validation(self):
        """
        Set validators on all matrix text edits (ensure integer input)
        :return:
        """
        validator = QIntValidator(0, 9999999999)
        for text_exit in self.kernel_matrix_edits:
            text_exit.setValidator(validator)
