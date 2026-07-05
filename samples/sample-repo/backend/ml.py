import tensorflow as tf


class Predictor:
    """Tiny TensorFlow example."""

    def build(self) -> tf.keras.Model:
        model = tf.keras.Sequential([tf.keras.layers.Dense(1)])
        model.compile(optimizer="adam", loss="mse")
        return model

