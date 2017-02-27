# -*- coding: utf-8 -*-

import argparse
import json
import subprocess

import numpy as np
import pandas as pd
import tensorflow as tf

PROJECT_ID = subprocess.check_output(
    "gcloud config list project --format 'value(core.project)'",
    shell=True
).rstrip()

FEATURES = [
    "sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday",
    "hourofday",
    "pickup_latitude", "pickup_longitude",
    "dropoff_latitude", "dropoff_longitude",
    "passenger_count",
    "estimated_distance"
]
OBJECTIVE = ["fare_amount"]

LEARNING_RATE = 0.0005

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--output_path", type=str)
args = parser.parse_args()


def inference(x_ph):
    hidden1 = tf.contrib.layers.fully_connected(x_ph, 16, activation_fn=tf.nn.relu6)
    hidden2 = tf.contrib.layers.fully_connected(hidden1, 8, activation_fn=tf.nn.relu6)
    logits = tf.contrib.layers.fully_connected(hidden2, 1, activation_fn=None)
    return logits


def build_loss(t_ph, logits):
    with tf.name_scope("rmse"):
        rmse = tf.sqrt(tf.reduce_mean(tf.squared_difference(t_ph, logits)))
    return rmse


if __name__ == "__main__":
    # Set log level
    tf.logging.set_verbosity(tf.logging.DEBUG)
    # Load dataset
    subprocess.call(["gsutil", "cp", "gs://cpb102demo1-ml/dataset/taxifare/*.csv", "/tmp/"])
    df_train = pd.read_csv("/tmp/taxi-feateng-train.csv")
    df_test = pd.read_csv("/tmp/taxi-feateng-test.csv")
    x_train, t_train = df_train[FEATURES].values, df_train[OBJECTIVE].values
    x_test, t_test = df_test[FEATURES].values, df_test[OBJECTIVE].values
    # Build graph
    x_ph = tf.placeholder(tf.float32, shape=[None, x_train.shape[1]])
    t_ph = tf.placeholder(tf.float32, shape=[None, 1])
    outputs = inference(x_ph)
    loss = build_loss(t_ph, outputs)
    optim = tf.train.AdamOptimizer(learning_rate=LEARNING_RATE).minimize(loss)
    init = tf.global_variables_initializer()
    saver = tf.train.Saver()

    # Start learning iterations
    with tf.Session() as sess:
        tf.summary.FileWriter("summary", graph=sess.graph)
        sess.run(init)
        for i in range(50000):
            # Show log every 100 iteration
            if i % 1000 == 0:
                tf.logging.info("iteration: {0}".format(i))
                fd = {x_ph: x_test, t_ph: t_test}
                tf.logging.info("test loss: {}".format(sess.run(loss, feed_dict=fd)))
                fd = {x_ph: x_train[:100], t_ph: t_train[:100]}
                tf.logging.info("training loss: {}".format(sess.run(loss, feed_dict=fd)))
            # Random sampling
            ind = np.random.choice(len(x_train), 256)
            sess.run(optim, feed_dict={x_ph: x_train[ind], t_ph: t_train[ind]})

        # Save variables
        saver.save(sess, "{}/model/export".format(args.output_path), write_meta_graph=False)
        # Define key element
        input_key = tf.placeholder(tf.int64, [None, ], name="key")
        output_key = tf.identity(input_key)
        # Define API inputs/outpus object
        inputs = {"key": input_key.name, "x": x_ph.name}
        outputs = {"key": output_key.name, "y": outputs.name}
        tf.add_to_collection("inputs", json.dumps(inputs))
        tf.add_to_collection("outputs", json.dumps(outputs))
        # Save graph
        saver.export_meta_graph(filename="{}/model/export.meta".format(args.output_path))
