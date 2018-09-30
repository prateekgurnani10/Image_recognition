import cv2
import numpy as np

# TODO: Move all image processing code into respective files along with using the Qt interface rather than openCV


class TrackbarOptions:
    contrast = "Contrast"
    brightness = "Brightness"
    filter = "Filter"
    grayscale = "Grayscale"


class MainWindow:
    _name = ''

    def __init__(self, name):
        self._img = name

    def get_name(self):
        return self._name

    def set_up(self, num_filtering_kernels):
        cv2.namedWindow(self._name)
        # Contrast must start at 1
        cv2.createTrackbar(TrackbarOptions.contrast, self._name, 0, 100, self.__bypass_on_change)
        # 50 is our zeroed point (> 50 is negative brightness)
        cv2.createTrackbar(TrackbarOptions.brightness, self._name, 50, 100, self.__bypass_on_change)
        # 0 - num of kernels to filter against
        cv2.createTrackbar(TrackbarOptions.filter, self._name, 0, num_filtering_kernels, self.__bypass_on_change)
        cv2.createTrackbar(TrackbarOptions.grayscale, self._name, 0, 1, self.__bypass_on_change)

    def __bypass_on_change(self, pos):
        pass


def main():
    img_path = "tests/images/test1.png"
    color_original = cv2.imread(img_path)
    if color_original is None:
        print(f"Invalid image filepath: {img_path}")
        exit(0)

    # Copy the colored image
    color_modified = color_original.copy()

    # Create/Copy the grayscale image
    gray_original = cv2.cvtColor(color_original, cv2.COLOR_BGR2GRAY)
    gray_modified = gray_original.copy()

    # Filter position 0 will automatically use the identity kernel
    identity_kernel = np.array([
        [0, 0, 0],
        [0, 1, 0],
        [0, 0, 0]
    ])

    sharpening_kernel = np.array([
        [0, -1,  0],
        [-1, 5, -1],
        [0, -1,  0]
    ])

    gaussian_kernel_1 = np.array([
        [1, 2, 1],
        [2, 4, 2],
        [1, 2, 1]
    ], np.float32) / 16

    # Get a gaussian using openCV
    gaussian_kernel_2 = cv2.getGaussianKernel(8, 0)  # Up 5 -> 8 for a more blurry effect

    # Another kernel for blurring
    box_kernel = np.array([
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ], np.float32) / 9  # Normalize the matrix by dividing by the number of total entries

    kernels = [identity_kernel, sharpening_kernel, gaussian_kernel_1, gaussian_kernel_2, box_kernel]

    window = MainWindow('app')
    window.set_up(len(kernels) - 1)

    count = 1  # Saved image count
    # UI loop
    while True:
        grayscale = cv2.getTrackbarPos(TrackbarOptions.grayscale, window.get_name())

        # Check to see if we want to show grayscale or colored image
        if grayscale == 1:
            cv2.imshow(window.get_name(), gray_modified)
        else:
            cv2.imshow(window.get_name(), color_modified)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            if grayscale == 1:
                # Save the image and update the saved image count
                cv2.imwrite(f"saved-{count}-{img_path}", gray_modified)
                print(f"Saving modified image")
                count += 1
            else:
                cv2.imwrite(f"saved-{count}-{img_path}", color_modified)
                print(f"Saving modified image")
                count += 1

        contrast = cv2.getTrackbarPos(TrackbarOptions.contrast, window.get_name())
        brightness = cv2.getTrackbarPos(TrackbarOptions.brightness, window.get_name())
        kernel_index = cv2.getTrackbarPos(TrackbarOptions.filter, window.get_name())

        if grayscale == 1:
            gray_modified = cv2.filter2D(gray_original, -1, kernels[kernel_index])
        else:
            color_modified = cv2.filter2D(color_original, -1, kernels[kernel_index])

        if grayscale == 1:
            gray_modified = cv2.addWeighted(gray_modified, contrast + 1, np.zeros(
                gray_original.shape, dtype=gray_original.dtype), 0, brightness - 50)
        else:
            color_modified = cv2.addWeighted(color_modified, contrast + 1, np.zeros(
                color_original.shape, dtype=color_original.dtype), 0, brightness - 50)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
