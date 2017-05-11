# -*- coding: utf-8 -*-

import argparse
import json
import os
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data


def inference(x_ph):
    with tf.variable_scope("hidden"):
        hidden = tf.layers.dense(x_ph, 20)
    with tf.variable_scope("output"):
        logits = tf.layers.dense(hidden, 10)
        y = tf.nn.softmax(logits)
    return y


def build_loss(y_ph, y):
    with tf.name_scope("loss"):
        cross_entropy = -tf.reduce_mean(y_ph * tf.log(y))
    return cross_entropy


def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=str)
    args, unknown_args = parser.parse_known_args()

    # Get ML Engine config from environment variable
    tf_conf = json.loads(os.environ.get("TF_CONFIG", "{}"))
    server = tf.train.Server(
        tf_conf["cluster"],
        job_name=tf_conf["task"]["type"],
        task_index=tf_conf["task"]["index"]
    )

    # Parameter server
    if tf_conf["task"]["type"] == "ps":
        server.join()

    # Create device function
    device_fn = tf.train.replica_device_setter(
        cluster=tf_conf["cluster"],
        worker_device="/job:{0}/task:{1}".format(tf_conf["task"]["type"], tf_conf["task"]["index"]),
    )

    # Load data set
    mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)

    # Build graph
    with tf.Graph().as_default() as g:
        with tf.device(device_fn):
            # Create placeholders
            x_ph = tf.placeholder(tf.float32, [None, 784])
            y_ph = tf.placeholder(tf.float32, [None, 10])
            # Build inference graph
            y = inference(x_ph)
            # Build loss graph
            cross_entropy = build_loss(y_ph, y)
            # Build other graph
            with tf.name_scope("accuracy"):
                correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_ph, 1))
                accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
            train_op = tf.train.GradientDescentOptimizer(1e-1).minimize(cross_entropy)
            init_op = tf.global_variables_initializer()
            if tf_conf["task"]["type"] == "master":
                tf.summary.FileWriter(logdir="mnist_summary", graph=g)

    # Start session
    with tf.Session(
        target=server.target,
        config=tf.ConfigProto(log_device_placement=False),
        graph=g,
    ) as sess:
        sess.run(init_op)
        for i in range(3001):
            x_train, y_train = mnist.train.next_batch(100)
            sess.run(train_op, feed_dict={x_ph: x_train, y_ph: y_train})
            if i % 100 == 0:
                train_loss = sess.run(cross_entropy, feed_dict={x_ph: x_train, y_ph: y_train})
                test_loss = sess.run(cross_entropy, feed_dict={x_ph: mnist.test.images, y_ph: mnist.test.labels})
                tf.logging.info("Iteration: {0} Training Loss: {1} Test Loss: {2}".format(i, train_loss, test_loss))
        test_accuracy = sess.run(accuracy, feed_dict={x_ph: mnist.test.images, y_ph: mnist.test.labels})
        tf.logging.info("Accuracy: {}".format(test_accuracy))
        # Only master save model for deployment on ML Engine
        if tf_conf["task"]["type"] == "master":
            input_key = tf.placeholder(tf.int64, [None, ], name="key")
            output_key = tf.identity(input_key)
            input_signatures = {
                "key": tf.saved_model.utils.build_tensor_info(input_key),
                "image": tf.saved_model.utils.build_tensor_info(x_ph)
            }
            output_signatures = {
                "key": tf.saved_model.utils.build_tensor_info(output_key),
                "score": tf.saved_model.utils.build_tensor_info(y)
            }
            predict_signature_def = tf.saved_model.signature_def_utils.build_signature_def(
                input_signatures,
                output_signatures,
                tf.saved_model.signature_constants.PREDICT_METHOD_NAME
            )
            builder = tf.saved_model.builder.SavedModelBuilder(os.path.join(args.model_dir, "model"))
            builder.add_meta_graph_and_variables(
                sess,
                [tf.saved_model.tag_constants.SERVING],
                signature_def_map={
                    tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: predict_signature_def
                },
                assets_collection=tf.get_collection(tf.GraphKeys.ASSET_FILEPATHS)
            )
            builder.save()


if __name__ == "__main__":
    main()
