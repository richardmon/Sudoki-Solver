#!/usr/bin/env python
# coding: utf-8

import matplotlib

matplotlib.use("Agg")
import io
import math
import matplotlib.pyplot as plt
import numpy as np
from skimage.filters import gaussian, threshold_local
from skimage.measure import find_contours, moments
from skimage.draw import line
from skimage.feature import corner_harris, corner_peaks
from skimage.color import gray2rgb
from skimage.io import imread
from PIL import Image
from images.utils import figure_to_PIL


def get_corners(image_path):
    """
    Get corners for of a given sudoku image.
    All the content of this LONG function comes from the jupyter-notebook
    with the same name.

    Returns:
        It returns a dictionary with the following shape:
        {
            'up_left': (48, 55),
            'down_left': (23, 337),
            'up_right': (322, 45),
            'down_right': (341, 341)
            'image': /tmp/path.to.image.jpg
        }
    """
    image = imread(image_path, as_gray=True)

    image_gauss = gaussian(image, 70, multichannel=False)  # Makes the image smoother
    block_size = 9
    local_thresh = threshold_local(image, block_size)
    binary_local = image_gauss > local_thresh

    contours = find_contours(binary_local, 0.9)

    # Taken from https://groups.google.com/forum/#!topic/scikit-image/--pXW-fPbGg
    def polygonArea(poly):
        """
        Return area of an unclosed polygon.

        :see: https://stackoverflow.com/a/451482
        :param poly: (n,2)-array
        """
        # we need a plain list for the following operations
        if isinstance(poly, np.ndarray):
            poly = poly.tolist()
        segments = zip(poly, poly[1:] + [poly[0]])
        return 0.5 * abs(sum(x0 * y1 - x1 * y0 for ((x0, y0), (x1, y1)) in segments))

    areas = map(polygonArea, contours)

    np_areas = np.array(list(areas))
    result = np.where(np_areas == np.amax(np_areas))
    max_index = result[0].item()
    black = binary_local > 256

    fig, ax = plt.subplots()

    ax.imshow(black, cmap=plt.cm.gray)
    contour = contours[max_index]

    ax.plot(contour[:, 1], contour[:, 0])

    im = figure_to_PIL(fig, ax, plt)

    img_only_borders = np.array(im)

    def rgb2gray(rgb):
        return np.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140])

    img_only_borders_grayscale = rgb2gray(img_only_borders)

    coords = corner_peaks(corner_harris(img_only_borders_grayscale), min_distance=2)

    def get_center_point(img):
        img_momentum = moments(img)
        center_x = img_momentum[1, 0] / img_momentum[0, 0]
        center_y = img_momentum[0, 1] / img_momentum[0, 0]

        return (center_x, center_y)

    def find_corner(img, coords):
        center_x, center_y = get_center_point(img)

        corners = {
            "up_left": [0, 0],
            "down_left": [0, 0],
            "up_right": [0, 0],
            "down_right": [0, 0],
        }
        distance = {"up_left": 0, "down_left": 0, "up_right": 0, "down_right": 0}

        for coord in coords:
            [y, x] = coord
            dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)

            if x < center_x and y < center_y and distance["up_left"] < dist:
                corners["up_left"] = [f"{x}", f"{y}"]
                distance["up_left"] = dist

            elif x > center_x and y < center_y and distance["up_right"] < dist:
                corners["up_right"] = [f"{x}", f"{y}"]
                distance["up_right"] = dist

            elif x > center_x and y > center_y and distance["down_right"] < dist:
                corners["down_right"] = [f"{x}", f"{y}"]
                distance["down_right"] = dist

            elif x < center_x and y > center_y and distance["down_left"] < dist:
                corners["down_left"] = [f"{x}", f"{y}"]
                distance["down_left"] = dist

            corners["image"] = image_path
            corners["image_shape"] = list(img.shape)

        return corners

    corners = find_corner(img_only_borders_grayscale, coords)
    return corners
