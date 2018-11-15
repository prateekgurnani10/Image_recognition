import cv2
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

IMAGE_DESCRIPT_DIALOG_UI = 'coreUI/image_description_dialog.ui'


class ImageDescriptionDialog(QDialog):
    """Image Description Dialog Window"""

    def __init__(self, image):
        super(ImageDescriptionDialog, self).__init__()
        loadUi(IMAGE_DESCRIPT_DIALOG_UI, self)

        # CV image that is passed to the dialog menu
        # Note: We do not want a dialog without an image to accompany it
        self._image = image
