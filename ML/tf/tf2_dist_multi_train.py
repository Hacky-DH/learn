# Keras traing with MultiWorkerMirroredStrategy in graph mode
import multiprocessing as mp
import numpy as np
import os

tf_config = '{"cluster":{"worker":["localhost:2222",\
        "localhost:2223"]},"task":{"type":"worker","index":%d}}'
replica_num = 2

def dist_run(replica_id, gpu_list):
    os.environ['TF_CONFIG'] = tf_config % replica_id
    os.environ['CUDA_VISIBLE_DEVICES'] = str(gpu_list)
    import tensorflow as tf

    strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()
    assert strategy.num_replicas_in_sync == 2, strategy.num_replicas_in_sync
    assert strategy.extended.worker_devices == (
            '/job:worker/replica:0/task:%d/device:GPU:0' % replica_id
            ,), strategy.extended.worker_devices
    assert strategy.extended._in_multi_worker_mode()

    x = np.asarray([[1, 2], [6, 12], [2, 4], [5, 10], [3, 6], [4, 8]])
    y = np.asarray([5, 4, 3, 2, 1, 0])

    with tf.Graph().as_default():
        assert not tf.distribute.in_cross_replica_context()
        assert tf.distribute.get_replica_context() is not None
        with strategy.scope():
            assert tf.distribute.get_replica_context() is None
            assert tf.distribute.in_cross_replica_context()
            assert tf.distribute.has_strategy()

            ds = tf.data.Dataset.from_tensor_slices((x,y)).repeat(2).batch(6)

            inputs = tf.keras.Input(shape=(2,))
            x = tf.keras.layers.Dense(4, activation=tf.nn.relu)(inputs)
            outputs = tf.keras.layers.Dense(1, activation=tf.nn.softmax)(x)
            model = tf.keras.Model(inputs=inputs, outputs=outputs)

            model.compile(
                    loss=tf.keras.losses.sparse_categorical_crossentropy,
                    optimizer=tf.keras.optimizers.SGD(learning_rate=0.001),
                    metrics=['accuracy'],
                    run_eagerly=False)
            assert model._distribution_strategy is not None
            assert not model.run_eagerly
        model.fit(x=ds, epochs=2)

def run():
    ctx = mp.get_context('fork')
    workers = []
    for i in range(replica_num):
        worker = ctx.Process(target=dist_run,
                args=(i,i))
        worker.start()
        workers.append(worker)
    for i in range(replica_num):
        workers[i].join()

run()
