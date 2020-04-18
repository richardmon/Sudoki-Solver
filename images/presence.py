#!/usr/bin/env python
import math
from skimage.filters import threshold_otsu
from skimage.transform import resize
from skimage.morphology import opening
from skimage.segmentation import clear_border
import numpy as np


def get_presence(image):
    # TODO: assert image is 306 x 306

    thresh = threshold_otsu(image)
    binary = image > thresh
    invert = np.invert(binary)
    opend = opening(invert)
    cleared = clear_border(opend)

    num_rows = 9
    num_cols = 9
    presence = np.zeros((num_rows, num_cols))
    max_mean = 0.05
    for i in range(num_rows):
        for j in range(num_cols):
            size = int(306 / 9)
            h = size * j
            w = size * i
            square = cleared[(size * i) : (i + 1) * size, j * size : (j + 1) * size]
            square_mean = np.mean(square)
            presence[i][j] = int(square_mean >= max_mean)

    job = {"image": image, "cleared": cleared, "presence": presence}
    return job
