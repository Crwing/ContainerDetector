import tensorflow as tf
import os
import tensorflow.contrib.data as tcd
import matplotlib.pyplot as plt

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


class tfrecords_reader:
    def __init__(self, path):
        self.tfrecord_path = path

    def _parse_function(self, example_proto):
        keys_to_features = {'train/image': tf.FixedLenFeature([], tf.string),
                            'train/label': tf.FixedLenFeature([2], dtype=tf.int64)}
        features = tf.parse_single_example(example_proto, features=keys_to_features)
        images = tf.decode_raw(features['train/image'], tf.uint8)
        labels = tf.cast(features['train/label'], tf.int32)
        images = tf.reshape(images, [28, 28, 3])
        return images, labels

    def main(self, batch):
        data_path = self.tfrecord_path + os.path.sep + 'bc.tfrecords'
        dataset = tcd.TFRecordDataset(data_path)
        dataset = dataset.map(self._parse_function)
        dataset = dataset.shuffle(buffer_size=10000)
        dataset = dataset.repeat()
        dataset = dataset.batch(batch)
        iterator = dataset.make_one_shot_iterator()
        image_batch, label_batch = iterator.get_next()
        with tf.Session() as sess:
            init_op = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())
            sess.run(init_op)
            coord = tf.train.Coordinator()
            threads = tf.train.start_queue_runners(coord=coord)
            images, labels = sess.run([image_batch, label_batch])
            coord.request_stop()
            coord.join(threads)

        return images, labels

    def _load_tfrecords(self):
        data_path = self.tfrecord_path + os.path.sep + 'bc.tfrecords'
        filename_queue = tf.train.string_input_producer([data_path], num_epochs=1, name='queue')
        reader = tf.TFRecordReader()
        _, serialized_example = reader.read(filename_queue)
        feature = {'train/image': tf.FixedLenFeature([], tf.string),
                   'train/label': tf.FixedLenFeature([2], dtype=tf.int64)}
        features = tf.parse_single_example(serialized_example, features=feature, name='features')
        return features

    @staticmethod
    def _get_data_label(features, batch):
        image = tf.decode_raw(features['train/image'], tf.uint8)
        label = tf.cast(features['train/label'], tf.int32)
        image = tf.reshape(image, [28, 28, 3])
        images, labels = tf.train.shuffle_batch([image, label],
                                                batch_size=batch,
                                                num_threads=4,
                                                capacity=50000,
                                                min_after_dequeue=10000)
        return images, labels

if __name__ == '__main__':
    path = os.path.abspath('../TFRecords')
    reader = tfrecords_reader(path)
    imgs, labels = reader.main(50)
    print(imgs.shape, labels.shape)
    plt.imshow(imgs[2])
    plt.show()
