# -*- coding: utf-8 -*-

import numpy as np
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data



def inference(x_ph):
    hidden = tf.layers.dense(x_ph, 20)
    logits = tf.layers.dense(hidden, 10)
    y = tf.nn.softmax(logits)
    return y


def build_loss(y_ph, y):
    cross_entropy = -tf.reduce_mean(y_ph * tf.log(y))
    return cross_entropy


def main():
    # Show TensorFlow version
    print(tf.__version__)
    # Set log level
    tf.logging.set_verbosity(tf.logging.INFO)
    # Load data set
    mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
    # Create placeholders
    x_ph = tf.placeholder(tf.float32, [None, 784])
    y_ph = tf.placeholder(tf.float32, [None, 10])
    # Build inference graph
    y = inference(x_ph)
    # Build loss graph
    cross_entropy = build_loss(y_ph, y)
    # Build other graph
    correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_ph, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    train_op = tf.train.GradientDescentOptimizer(1e-1).minimize(cross_entropy)
    init_op = tf.global_variables_initializer()
    # Start session
    with tf.Session(config=tf.ConfigProto(log_device_placement=True)) as sess:
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

if __name__ == "__main__":
    main()
