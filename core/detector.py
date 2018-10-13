import cv2
from utils import processing_utils as utils


class Detector:
    def __init__(self):
        self._num_faces = 0                 # Number of faces detected
        self._cascades = utils.Cascades()   # Mapping of cascades to their cascade classifiers

    def faces(self):
        """
        Number of faces
        :return: Number of faces detected
        """
        return self._num_faces

    def detect(self, image_g, image_d):
        """
        Detect face and eyes in an image
        :param image_g: Grayscale image
        :param image_d: Detected image
        :return: A detected image with rectangles drawn around faces and eyes
        """
        # Detect faces
        faces = self._cascades.cascades_list[utils.Cascades.CascadeList.FACE_CASCADE].detectMultiScale(image_g, 1.3, 5)
        self._num_faces = len(faces)

        for (x, y, w, h) in faces:
            cv2.rectangle(image_d, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Regions of interest (grayscale and color)
            roi_grayscale = image_g[y: y + h, x: x + w]
            roi_color = image_d[y: y + h, x: x + w]

            # Detect eyes
            eyes = self._cascades.cascades_list[utils.Cascades.CascadeList.EYE_CASCADE].detectMultiScale(
                roi_grayscale, 1.1, 22)

            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

        return image_d
