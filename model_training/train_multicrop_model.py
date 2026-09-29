from pathlib import Path
import json
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "multicrop_dataset"
ARTIFACTS_DIR = BASE_DIR / "artifacts"

TRAIN_DIR = DATA_DIR / "train"
VAL_DIR = DATA_DIR / "validation"
TEST_DIR = DATA_DIR / "test"

IMG_SIZE = (160, 160)
BATCH_SIZE = 16
EPOCHS = 10
SEED = 42

# Check dataset directories
for folder in (TRAIN_DIR, VAL_DIR, TEST_DIR):
    if not folder.exists():
        raise SystemExit(f"Dataset folder missing: {folder}")

# Load datasets
train_ds = keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="int",
    shuffle=True,
    seed=SEED
)

val_ds = keras.utils.image_dataset_from_directory(
    VAL_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="int",
    shuffle=False
)

test_ds = keras.utils.image_dataset_from_directory(
    TEST_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="int",
    shuffle=False
)

class_names = train_ds.class_names
num_classes = len(class_names)

# Ensure same class folders in every split
for split_name, split_ds in (("validation", val_ds), ("test", test_ds)):
    if split_ds.class_names != class_names:
        raise SystemExit(
            f"Class folder mismatch in {split_name}.\n"
            f"Train: {class_names}\n"
            f"{split_name}: {split_ds.class_names}"
        )

print("\nClasses:")
for index, name in enumerate(class_names):
    print(f"{index}: {name}")

# Save class mapping
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
with open(ARTIFACTS_DIR / "class_names.json", "w", encoding="utf-8") as file:
    json.dump(class_names, file, indent=2, ensure_ascii=False)

# Improve input pipeline
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.prefetch(AUTOTUNE)
val_ds = val_ds.prefetch(AUTOTUNE)
test_ds = test_ds.prefetch(AUTOTUNE)

# Data augmentation
augmentation = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.08),
    layers.RandomZoom(0.10),
], name="data_augmentation")

# Pretrained feature extractor
base_model = keras.applications.MobileNetV2(
    input_shape=IMG_SIZE + (3,),
    include_top=False,
    weights="imagenet"
)
base_model.trainable = False

inputs = keras.Input(shape=IMG_SIZE + (3,))
x = augmentation(inputs)
x = keras.applications.mobilenet_v2.preprocess_input(x)
x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.25)(x)
outputs = layers.Dense(num_classes, activation="softmax")(x)

model = keras.Model(inputs, outputs)

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.0005),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

callbacks = [
    keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=3,
        restore_best_weights=True
    ),
    keras.callbacks.ModelCheckpoint(
        filepath=str(ARTIFACTS_DIR / "best_crop_model.keras"),
        monitor="val_loss",
        save_best_only=True
    )
]

print("\nStarting training...")
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    callbacks=callbacks
)

print("\nEvaluating on test dataset...")
test_loss, test_accuracy = model.evaluate(test_ds, verbose=1)
print(f"Test loss: {test_loss:.4f}")
print(f"Test accuracy: {test_accuracy:.4f}")

final_path = ARTIFACTS_DIR / "crop_disease_model.keras"
model.save(final_path)

print("\nTRAINING COMPLETE")
print(f"Model saved: {final_path}")
print(f"Class labels saved: {ARTIFACTS_DIR / 'class_names.json'}")
