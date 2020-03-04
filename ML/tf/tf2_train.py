# linear regression with keras
import tensorflow as tf
assert tf.version.VERSION >= '2.0.1'
from tensorflow.keras import layers
# create model
model = tf.keras.Sequential()
model.add(layers.Dense(8, input_dim=2, activation='relu')) # tf.nn.relu
model.add(layers.Dense(4, activation='relu'))
model.add(layers.Dense(1, activation='linear'))

model.compile(optimizer=tf.keras.optimizers.Adam(0.001),
              loss=tf.losses.mse, metrics=['accuracy'])

# create dataset
data = tf.random.uniform((1024,2), minval=1, maxval=100, dtype=tf.int32)
labels = tf.random.uniform((1024,1), minval=0, maxval=1, dtype=tf.int32)
ds = tf.data.Dataset.from_tensor_slices((data, labels))
ds = ds.batch(64).repeat()

# train
model.fit(ds, epochs=10, steps_per_epoch=30)
