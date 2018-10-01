from abc import ABCMeta, abstractmethod


class ImageProcessor:
    """ Abstract class for behavior based image processing.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def process_image(self, image, behavior):
        pass


# Kernel filtering
class FilterProcessor(ImageProcessor):
    def __init__(self):
        pass

    def process_image(self, image, behavior):
        pass


class BrightnessProcessor(ImageProcessor):
    def __init__(self):
        pass

    def process_image(self, image, behavior):
        pass


class ContrastProcessor(ImageProcessor):
    def __init__(self):
        pass

    def process_image(self, image, behavior):
        pass

