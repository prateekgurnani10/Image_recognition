import cv2
import pytest
from core import detector


@pytest.mark.parametrize("image_file_path, expected_outcome", [
    ("images/test_facial_recognition.jpg", 2),
    ("images/tfr_3_many_faces.jpg", 24),
    ("images/tfr_4_facial_expressions.jpg", 18),
    ("images/tfr_6_no_faces.jpg", 0),
    ("images/tfr_7_no_faces_2.jpg", 0),
    ("images/tfr_8_turned_around.jpg", 0)
])
def test_detect(image_file_path, expected_outcome):
    color_img = cv2.imread(image_file_path)
    if color_img is None:
        print("Image path not recognized")
        assert False

    grayscale_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)
    facial_recog = detector.Detector()
    _ = facial_recog.detect(grayscale_img, color_img)
    assert facial_recog.faces() == expected_outcome
