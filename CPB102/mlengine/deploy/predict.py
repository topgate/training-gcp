# -*- coding: utf-8 -*-

import argparse
from tensorflow.examples.tutorials.mnist import input_data
import numpy as np
from oauth2client.client import GoogleCredentials
from googleapiclient import discovery

parser = argparse.ArgumentParser()
parser.add_argument("--project", type=str)
parser.add_argument("--model", type=str)
args, unknown_args = parser.parse_known_args()

PROJECT_NAME = args.project
MODEL_NAME = args.model

mnist = input_data.read_data_sets("MNIST_data/", one_hot=False)
x_batch, y_batch = mnist.train.next_batch(3)

print("Call ML model on Cloud ML Engine...")
credentials = GoogleCredentials.get_application_default()
ml = discovery.build("ml", "v1", credentials=credentials)
data = {
    "instances": [
        {"image": x_batch[0].tolist(), "key": 0},
        {"image": x_batch[1].tolist(), "key": 1},
        {"image": x_batch[2].tolist(), "key": 2},
    ]
}
req = ml.projects().predict(
    body=data,
    name="projects/{0}/models/{1}/versions/v1".format(PROJECT_NAME, MODEL_NAME)
)
res = req.execute()
print(res)

for i in range(3):
    print("Prediction: {0} True: {1}".format(np.argmax(res["predictions"][i]["score"]), y_batch[i]))
