import sys
import numpy as np
import tensorflow as tf
from tensorflow.python.client import timeline
from tensorflow.core.protobuf import config_pb2

run_options = config_pb2.RunOptions(
	trace_level=config_pb2.RunOptions.FULL_TRACE)
run_metadata = config_pb2.RunMetadata()


with tf.Graph().as_default():
    ip = tf.keras.layers.Input([2])
    h = tf.keras.layers.Dense(10, activation='relu',
    	input_dim=2)(ip)
    out = tf.keras.layers.Dense(2, activation='softmax')(h)

    model = tf.keras.models.Model(inputs=[ip], outputs=[out])

    model.compile(optimizer='Adam',
        loss='categorical_crossentropy',
        options=run_options,
        run_metadata=run_metadata)

    x = np.random.randn(100, 2)
    y = (x[:, 0] * x[:, 1]) > 0

    model.fit(x, tf.keras.utils.to_categorical(y), epochs=1)

    if run_metadata.step_stats.ByteSize():
        trace = timeline.Timeline(step_stats=run_metadata.step_stats)
        with open('timeline_benchmark.json', 'w') as f:
            f.write(trace.generate_chrome_trace_format())
