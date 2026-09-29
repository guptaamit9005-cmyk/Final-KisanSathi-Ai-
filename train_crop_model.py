from pathlib import Path

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

TRAIN_DIR = BASE_DIR / "dataset" / "train"
VALIDATION_DIR = BASE_DIR / "dataset" / "validation"

MODEL_DIR = BASE_DIR / "prediction" / "ml_models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "crop_disease_model.keras"


# ============================================================
# SETTINGS
# ============================================================

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10
SEED = 42


# ============================================================
# CHECK DIRECTORIES
# ============================================================

print("=" * 70)
print("KISANSATHI AI - CROP DISEASE MODEL TRAINING")
print("=" * 70)

print("\nTrain directory:")
print(TRAIN_DIR)

print("\nValidation directory:")
print(VALIDATION_DIR)

if not TRAIN_DIR.exists():
    raise FileNotFoundError(
        f"Training folder not found:\n{TRAIN_DIR}"
    )

if not VALIDATION_DIR.exists():
    raise FileNotFoundError(
        f"Validation folder not found:\n{VALIDATION_DIR}"
    )


# ============================================================
# LOAD TRAINING DATA
# ============================================================

train_dataset = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=True,
    seed=SEED,
)


# ============================================================
# LOAD VALIDATION DATA
# ============================================================

validation_dataset = tf.keras.utils.image_dataset_from_directory(
    VALIDATION_DIR,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False,
)


# ============================================================
# CLASS NAMES
# ============================================================

class_names = train_dataset.class_names

print("\n" + "=" * 70)
print("CLASSES")
print("=" * 70)

for i, class_name in enumerate(class_names):
    print(f"{i}: {class_name}")

print("\nTotal classes:", len(class_names))


# ============================================================
# VERIFY TRAIN / VALIDATION CLASSES
# ============================================================

validation_classes = validation_dataset.class_names

if class_names != validation_classes:

    raise ValueError(
        "\nTraining and validation class names do not match.\n"
        f"Training: {class_names}\n"
        f"Validation: {validation_classes}"
    )


# ============================================================
# PERFORMANCE
# ============================================================

AUTOTUNE = tf.data.AUTOTUNE

train_dataset = train_dataset.prefetch(
    buffer_size=AUTOTUNE
)

validation_dataset = validation_dataset.prefetch(
    buffer_size=AUTOTUNE
)


# ============================================================
# DATA AUGMENTATION
# ============================================================

data_augmentation = keras.Sequential(
    [
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.1),
    ],
    name="data_augmentation",
)


# ============================================================
# MOBILE NET V2
# ============================================================

base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet",
)

base_model.trainable = False


# ============================================================
# MODEL
# ============================================================

inputs = keras.Input(
    shape=(224, 224, 3)
)

x = data_augmentation(inputs)

x = tf.keras.applications.mobilenet_v2.preprocess_input(x)

x = base_model(
    x,
    training=False
)

x = layers.GlobalAveragePooling2D()(x)

x = layers.Dropout(0.30)(x)

outputs = layers.Dense(
    len(class_names),
    activation="softmax"
)(x)

model = keras.Model(
    inputs=inputs,
    outputs=outputs
)


# ============================================================
# COMPILE
# ============================================================

model.compile(
    optimizer=keras.optimizers.Adam(
        learning_rate=0.0001
    ),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)


# ============================================================
# MODEL SUMMARY
# ============================================================

print("\n")
model.summary()


# ============================================================
# CALLBACKS
# ============================================================

callbacks = [

    keras.callbacks.ModelCheckpoint(
        filepath=str(MODEL_PATH),
        monitor="val_accuracy",
        save_best_only=True,
        verbose=1
    ),

    keras.callbacks.EarlyStopping(
        monitor="val_accuracy",
        patience=3,
        restore_best_weights=True,
        verbose=1
    )
]


# ============================================================
# TRAIN
# ============================================================

print("\n" + "=" * 70)
print("STARTING TRAINING")
print("=" * 70)

history = model.fit(
    train_dataset,
    validation_data=validation_dataset,
    epochs=EPOCHS,
    callbacks=callbacks,
)


# ============================================================
# FINAL SAVE
# ============================================================

model.save(
    MODEL_PATH
)


# ============================================================
# RESULT
# ============================================================

print("\n" + "=" * 70)
print("TRAINING COMPLETED")
print("=" * 70)

print("\nModel saved at:")

print(MODEL_PATH)

if MODEL_PATH.exists():

    size_mb = MODEL_PATH.stat().st_size / (
        1024 * 1024
    )

    print(
        f"\nModel size: {size_mb:.2f} MB"
    )

print("\nFinal classes:")

for i, class_name in enumerate(class_names):

    print(
        f"{i}: {class_name}"
    )

print("\nKisanSathi AI crop disease model is ready.")