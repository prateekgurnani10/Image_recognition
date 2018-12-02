from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi


IMAGE_DESCRIPT_DIALOG_UI = 'coreUI/webcam_dialog.ui'


class WebcamDialog(QDialog):
    """Webcam Dialog Window"""

    def __init__(self):
        super(WebcamDialog, self).__init__()
        loadUi(IMAGE_DESCRIPT_DIALOG_UI, self)
