import tensorflow as tf

from tensorflow.keras.preprocessing.image import ImageDataGenerator

IMG_SIZE = 224

BATCH_SIZE = 32

train_data = ImageDataGenerator(

    rescale=1/255,

    validation_split=0.2

)

train = train_data.flow_from_directory(

    "dataset/PlantVillage",

    target_size=(IMG_SIZE, IMG_SIZE),

    batch_size=BATCH_SIZE,

    subset="training"

)

val = train_data.flow_from_directory(

    "dataset/PlantVillage",

    target_size=(IMG_SIZE, IMG_SIZE),

    batch_size=BATCH_SIZE,

    subset="validation"

)

base = tf.keras.applications.EfficientNetB0(

    include_top=False,

    weights="imagenet",

    input_shape=(224,224,3)

)

base.trainable=False

model = tf.keras.Sequential([

    base,

    tf.keras.layers.GlobalAveragePooling2D(),

    tf.keras.layers.Dropout(0.3),

    tf.keras.layers.Dense(

        train.num_classes,

        activation="softmax"

    )

])

model.compile(

    optimizer="adam",

    loss="categorical_crossentropy",

    metrics=["accuracy"]

)

model.fit(

    train,

    validation_data=val,

    epochs=10

)

model.save("ai_model/model/crop_model.keras")