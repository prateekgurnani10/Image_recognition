from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi


#################################################################
# Globals
SLIDER_WIDGET_UI = 'slider_widget.ui'

#################################################################


class SliderWidget(QWidget):

    def __init__(self):
        super(QWidget, self).__init__()
        loadUi(SLIDER_WIDGET_UI, self)
