#!/usr/bin/env python
# coding: utf-8

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skimage.io import imread
from skimage.transform import resize
import numpy as np
import skimage.transform as tf
from PIL import Image
from io import BytesIO
from images.utils import figure_to_PIL


def transform(corners):
    """
    This function is based in the jupyter notebook with the same name.
    Look at it for documentation.
    """
    image_path = corners["image"]
    image = imread(image_path, as_gray=True)
    image_shape = tuple(corners["image_shape"])
    image_resize = resize(image, image_shape, mode="symmetric", preserve_range=True)

    # Given that the new shape will be 300 by 300 this is the given points
    src = np.array([[0, 0], [0, 300], [300, 300], [300, 0]])

    corners["up_left"] = [float(x) for x in corners["up_left"]]
    corners["down_left"] = [float(x) for x in corners["down_left"]]
    corners["up_right"] = [float(x) for x in corners["up_right"]]
    corners["down_right"] = [float(x) for x in corners["down_right"]]

    dst = np.array(
        [
            corners["up_left"],
            corners["down_left"],
            corners["down_right"],
            corners["up_right"],
        ]
    )

    tform = tf.ProjectiveTransform()
    tform.estimate(src, dst)
    warped = tf.warp(image_resize, tform, output_shape=image_shape)

    new_image = warped[0:300, 0:300]

    fig, ax = plt.subplots()

    ax.imshow(new_image, cmap=plt.cm.gray)

    divisor = 299
    color = "#FF0000"

    for i in range(9):
        x = (divisor / 9) * (i + 1)
        y1 = 0
        y2 = 299
        linewidth = int((i + 1) % 3 == 0) * 3 or 1
        plt.plot([x, x], [y1, y2], "-", linewidth=linewidth, color=color)
        plt.plot([y1, y2], [x, x], "-", linewidth=linewidth, color=color)
    plt.plot([0, 0], [0, divisor], "-", linewidth=3, color=color)
    plt.plot([0, divisor], [0, 0], "-", linewidth=3, color=color)

    pil_image = figure_to_PIL(fig, ax, plt)

    response = {
        "image": pil_image,
        "transform_image": new_image
        }

    return response
