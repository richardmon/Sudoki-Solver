import collections
import numpy as np

import matplotlib.pyplot as plt

from .prediction import predict

COUNT_PREDICTION = 3


def inference(list_images, original_image, presence_matrix):
    """ Takes a list of images and makes a predicion for each one of it  """
    predictions = []
    for i, image in enumerate(list_images):
        predicted = np.array([])
        for count in range(COUNT_PREDICTION):
            estimated_number = predict(image)
            predicted = np.append(predicted, [estimated_number])
        counters = collections.Counter(predicted)
        most_common = counters.most_common(1)
        predictions.append(most_common)
    return {
        "predictions": predictions,
        "original_image": original_image,
        "presence": presence_matrix,
    }
