import cv2
import numpy as np


IMG_SIZE = 224


def preprocess_crop_image(image_path):
    """
    OpenCV preprocessing pipeline.

    Steps:
    1. Read image
    2. Validate image
    3. Convert BGR -> RGB
    4. Resize
    5. Mild denoising
    6. Improve contrast
    7. Normalize
    """

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Unable to read uploaded image.")

    # BGR -> RGB
    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    # Resize
    image = cv2.resize(
        image,
        (IMG_SIZE, IMG_SIZE),
        interpolation=cv2.INTER_AREA
    )

    # Mild denoising
    image = cv2.GaussianBlur(
        image,
        (3, 3),
        0
    )

    # Convert to LAB for controlled contrast
    lab = cv2.cvtColor(
        image,
        cv2.COLOR_RGB2LAB
    )

    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    l_channel = clahe.apply(
        l_channel
    )

    lab = cv2.merge(
        [l_channel, a_channel, b_channel]
    )

    image = cv2.cvtColor(
        lab,
        cv2.COLOR_LAB2RGB
    )

    # Normalize
    image = image.astype(
        np.float32
    ) / 255.0

    # Batch dimension
    image = np.expand_dims(
        image,
        axis=0
    )

    return image