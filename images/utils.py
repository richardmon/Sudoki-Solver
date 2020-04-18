from PIL import Image
import numpy as np
import matplotlib
from io import BytesIO

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def np_array_to_PIL_image(np_image: np.array) -> Image:
    fig, ax = plt.subplots()
    ax.imshow(np_image, cmap=plt.cm.gray)
    return figure_to_PIL(fig, ax)


def figure_to_PIL(
    figure: matplotlib.figure.Figure, axis: matplotlib.axes.Axes, plt=plt
) -> Image:
    plt.axis("off")
    axis.set_yticklabels([])
    axis.set_xticklabels([])
    buf = BytesIO()
    figure.savefig(buf, format="JPEG", bbox_inches="tight", pad_inches=0)
    buf.seek(0)
    im = Image.open(buf)
    return im
