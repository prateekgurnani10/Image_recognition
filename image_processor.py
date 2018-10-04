from abc import ABCMeta, abstractmethod


class ImageProcessor:
    """ Abstract class for behavior based image processing.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def process_image(self, image):
        pass

    @abstractmethod
    def behavior(self):
        pass


# Kernel filtering
class FilterProcessor(ImageProcessor):
    def __init__(self, behavior):
        self._behavior = behavior

    def process_image(self, image):
        pass

    def behavior(self):
        return self._behavior


class BrightnessProcessor(ImageProcessor):
    def __init__(self, behavior):
        self._behavior = behavior

    def process_image(self, image):
        pass

    def behavior(self):
        return self._behavior


class ContrastProcessor(ImageProcessor):
    def __init__(self, behavior):
        self._behavior = behavior

    def process_image(self, image):
        pass

    def behavior(self):
        return self._behavior
