import cv2
import pytest
from core import image_processor
from utils import processing_utils


@pytest.mark.parametrize("image_file_path", [
    "images/test_facial_recognition.jpg",
    "images/tfr_3_many_faces.jpg",
    "images/tfr_4_facial_expressions.jpg",
    "images/tfr_6_no_faces.jpg",
    "images/tfr_7_no_faces_2.jpg",
    "images/tfr_8_turned_around.jpg"
])
def test_detect(image_file_path):
    color_img = cv2.imread(image_file_path)
    if color_img is None:
        print("Image path not recognized")
        assert False

    test_behavior = processing_utils.ProcessingBehavior((0, 100), "test", 50)
    # Ensure test_behavior is properly created
    assert test_behavior.min_max == (0, 100)

    processors_list = [
        image_processor.ContrastProcessor(test_behavior),
        image_processor.BrightnessProcessor(test_behavior)
    ]

    for processor in processors_list:
        # Copy a new image before every processor is applied to ensure a change in shape relative
        # to the original image occurs
        image_in = color_img.copy()
        image_out = color_img.copy()

        # Use the image as both the unprocessed and processed in this case
        processor.set_unique_value(20)
        image_out = processor.process_image(image_in, image_out)

        assert image_in.shape == image_out.shape
