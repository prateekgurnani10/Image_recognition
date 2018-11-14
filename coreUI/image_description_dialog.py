import cv2
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

IMAGE_DESCRIPT_DIALOG_UI = 'coreUI/image_description_dialog.ui'


class ImageDescriptionDialog(QDialog):
    """Image Description Dialog Window"""

    def __init__(self):
        super(ImageDescriptionDialog, self).__init__()
        loadUi(IMAGE_DESCRIPT_DIALOG_UI, self)
        self.show()
