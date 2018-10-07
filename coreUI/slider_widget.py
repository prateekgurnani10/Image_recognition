from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal


# UI form
SLIDER_WIDGET_UI = 'coreUI/slider_widget.ui'


class SliderWidget(QWidget):

    # Behavior signal relay
    # Emits (behavior name, slider value)
    slider_moved = pyqtSignal(str, int)

    def __init__(self, behavior):
        super(QWidget, self).__init__()
        loadUi(SLIDER_WIDGET_UI, self)

        # Slider behavior model parameters
        self._behavior = behavior
        self._setting_info = behavior.setting_info
        (min_v, max_v) = behavior.min_max
        # Default slider position
        self._default_slider_pos = behavior.default

        # Set slider min/max based on the behavior
        self.behaviorSlider.setMinimum(min_v)
        self.behaviorSlider.setMaximum(max_v)

        # Set default slider position based on the behavior
        self.behaviorSlider.setValue(self._default_slider_pos)

        # Set labels name/value according to the given behavior
        self.behaviorLabel.setText(behavior.name)
        self.sliderValueLabel.setText(str(self.behaviorSlider.value()))

        if len(self._setting_info) > 0:
            self.infoLabel.setText(self._setting_info[0])

        self.behaviorSlider.valueChanged.connect(self.on_slider_value_changed)

    @pyqtSlot()
    def on_slider_value_changed(self):
        # Update value label when the slider is moved
        self.sliderValueLabel.setText(str(self.behaviorSlider.value()))

        if len(self._setting_info) > 0:
                self.infoLabel.setText(self._setting_info[self.behaviorSlider.value()])

        self.slider_moved.emit(self._behavior.name, self.behaviorSlider.value())
