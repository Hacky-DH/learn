# tf 2.1.0
# use MirroredStrategy with MonitoredTrainingSession in graph mode
import tensorflow as tf
import tensorflow.compat.v1 as tf1
import numpy as np

strategy = tf.distribute.MirroredStrategy(["/gpu:0", "/gpu:1"])
assert strategy.num_replicas_in_sync == 2
assert strategy.extended.worker_devices == (
    '/job:localhost/replica:0/task:0/device:GPU:0',
    '/job:localhost/replica:0/task:0/device:GPU:1'
    ), strategy.extended.worker_devices

def run(monitor):
    session = tf1.train.MonitoredTrainingSession if monitor else tf1.Session
    print('Run with', session.__name__)

    with tf.Graph().as_default(), strategy.scope():
        x = np.asarray([[1, 2], [6, 12], [2, 4], [5, 10], [3, 6], [4, 8]])
        y = np.asarray([5, 4, 3, 2, 1, 0])

        ds = tf1.data.Dataset.from_tensor_slices((x,y)).repeat(2).batch(6)
        ds = strategy.experimental_distribute_dataset(ds)
        iterator = tf1.data.make_initializable_iterator(ds)
        init = iterator.initialize()

        x, y = strategy.experimental_run(lambda z: z, iterator)
        x, y = strategy.experimental_local_results(x),\
                strategy.experimental_local_results(y)

        with session() as sess:
            for _ in range(2):
                sess.run(init)
                x_, y_ = sess.run([x, y])
                assert x_[0].tolist() == [[1, 2], [6, 12], [2, 4]]
                assert x_[1].tolist() == [[5, 10], [3, 6], [4, 8]]
                assert y_[0].tolist() == [5, 4, 3]
                assert y_[1].tolist() == [2, 1, 0]

run(False)
run(True)
