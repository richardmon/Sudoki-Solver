"""
Author: Richard Montoya
Date: 2019-10-29

Module for extracting the number contain in an image,
for the current implementation, only one number would be process per image.
"""

from torchvision import transforms
import torch

from .Network import Net

from skimage.transform import resize
from skimage.util import invert


if torch.cuda.is_available():
    device = torch.device('cuda')
else:
    device = torch.device('cpu')

network = Net()
model_state = torch.load('models/model.pth')
network.load_state_dict(model_state)
network.double()
network.to(device=device)

normalize = transforms.Normalize((0.1307,), (0.3081,))
# Transformer
transformer_eval = transforms.Compose([
    transforms.ToTensor(),
    normalize
])

def predict(image_input, should_invert=False):
    """
    Process an image and provides a prediction for the number in it.

    :param image_input: Image to be process
    :param should_invert: True if the colors should be inverted, default False
    """
    assert len(image_input.shape) == 2, "The image should be in grayscale"
    size = (28, 28)

    image = resize(image_input, size, anti_aliasing=True)
    if should_invert:
        image = invert(image)

    tranfomed_image = transformer_eval(image)
    batch_image = tranfomed_image.unsqueeze(0).to(device=device)

    assert len(batch_image.shape) == 4, f"Wrong batch dimensions, expected 4, got {len(batch_image.shape)}"

    output = network(batch_image)

    pred = output.data.max(1)[1][0].item()

    return pred
