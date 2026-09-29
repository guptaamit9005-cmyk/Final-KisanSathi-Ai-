"""
Trains the crop-disease classifier using transfer learning on MobileNetV2.
Run this ONCE (outside the Django request cycle) to produce
ml_model/crop_disease_model.h5, which predictor.py then loads.

Dataset layout expected (standard PlantVillage-style structure):

    dataset/
        train/
            Tomato_healthy/
                img1.jpg
                img2.jpg
            Tomato_Early_blight/
                ...
            Potato___Late_blight/
                ...
        val/
            Tomato_healthy/
                ...
            ...

Download a PlantVillage-style dataset (e.g. from Kaggle) and arrange it
this way, then run:

    python train_model.py --data_dir ./dataset --epochs 15

This is a one-time offline step — it does NOT run inside the web app.
"""

import argparse
import os

from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator

IMG_SIZE = (224, 224)
BATCH_SIZE = 32


def build_model(num_classes):
    base = MobileNetV2(input_shape=(*IMG_SIZE, 3), include_top=False, weights="imagenet")
    base.trainable = False  # freeze the pretrained backbone

    x = base.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation="relu")(x)
    x = Dropout(0.3)(x)
    output = Dense(num_classes, activation="softmax")(x)

    model = Model(inputs=base.input, outputs=output)
    model.compile(optimizer=Adam(learning_rate=1e-3), loss="categorical_crossentropy", metrics=["accuracy"])
    return model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", required=True, help="Path to dataset/ folder containing train/ and val/")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--out", default=os.path.join("ml_model", "crop_disease_model.h5"))
    args = parser.parse_args()

    train_dir = os.path.join(args.data_dir, "train")
    val_dir = os.path.join(args.data_dir, "val")

    train_gen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=20,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.15,
        horizontal_flip=True,
    ).flow_from_directory(train_dir, target_size=IMG_SIZE, batch_size=BATCH_SIZE, class_mode="categorical")

    val_gen = ImageDataGenerator(rescale=1.0 / 255).flow_from_directory(
        val_dir, target_size=IMG_SIZE, batch_size=BATCH_SIZE, class_mode="categorical"
    )

    num_classes = train_gen.num_classes
    model = build_model(num_classes)

    model.fit(train_gen, validation_data=val_gen, epochs=args.epochs)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    model.save(args.out)

    # IMPORTANT: copy this printed list, in this exact order, into
    # ml_model/predictor.py's CLASS_NAMES and ml_model/disease_data.py's keys.
    class_indices = train_gen.class_indices
    ordered_classes = [name for name, idx in sorted(class_indices.items(), key=lambda kv: kv[1])]
    print("\nModel saved to:", args.out)
    print("\nCLASS_NAMES (copy this order into predictor.py):")
    print(ordered_classes)


if __name__ == "__main__":
    main()