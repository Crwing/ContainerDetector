import tensorflow as tf
import os

import_path = os.path.abspath('../module/bc-cnn/500')
export_path = os.path.abspath('../frozen_module/bc-cnn')


def main():
    dir(tf.contrib)
    output_graph = export_path + "/frozen_model.pb"
    output_node_names = 'x,output/predict_sm,keep_prob'
    with tf.Session(graph=tf.Graph()) as sess:
        saver = tf.train.import_meta_graph(import_path + '/binary_classification_CNN.ckpt.meta')
        saver.restore(sess, import_path + '/binary_classification_CNN.ckpt')
        output_graph_def = tf.graph_util.convert_variables_to_constants(sess, tf.get_default_graph().as_graph_def(),
                                                                        output_node_names.split(","))

        with tf.gfile.GFile(output_graph, "wb") as f:
            f.write(output_graph_def.SerializeToString())
        print("%d ops in the final graph." % len(output_graph_def.node))
    return output_graph_def


if __name__ == '__main__':
    main()
