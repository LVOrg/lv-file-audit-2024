import os
os.environ["CUDA_VISIBLE_DEVICES"]="0"
import torch
import torchvision.transforms as transforms
from torchvision.datasets import ImageFolder
from torchvision.models import resnet18
from torch.utils.data import DataLoader
from  PIL import Image
import numpy as np

def convert_image_to_tensor(img):
    """Converts an image to a tensor.

    Args:
        img: The image to convert.

    Returns:
        The image tensor.
    """

    transform = transforms.Compose([transforms.PILToTensor()])
    tensor = transform(img)
    return tensor
def classify_image(image_path):
    """Classifies an image as an invoice, credit card, etc.

    Args:
        image_path: The path to the image to be classified.

    Returns:
        The class of the image.
    """

    # Load the image and convert it to a tensor.
    # image = convert_image_to_tensor(Image.open(image_path).convert('RGB'))
    # image = torch.from_numpy(
    #     torch.as_tensor(
    #         Image.open(image_path).convert('RGB'))
    # ).float()
    image = torch.from_numpy(
        np.asarray(Image.open(image_path))
        # convert_image_to_tensor(Image.open(image_path).convert('RGB'))
    ).float()
    # Resize the image to 224x224.
    image = transforms.Resize(128,antialias=None)(image)
    #
    # # Center the image.
    image = transforms.CenterCrop(128)(image)

    # Normalize the image.
    image = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])(image)

    # Load the pre-trained ResNet18 model.
    model = resnet18(pretrained=True)

    # Classify the image.
    output = model(image)

    # Get the class with the highest probability.
    class_index = output.argmax()

    # Get the class name.
    class_name = ImageFolder.CLASSES[class_index]

    return class_name

if __name__ == '__main__':
    # Get the image path.
    image_path = '/home/vmadmin/python/v6/file-service-02/bard/image-files/2285.jpg'

    # Classify the image.
    class_name = classify_image(image_path)

    print('The image is classified as a {}.'.format(class_name))