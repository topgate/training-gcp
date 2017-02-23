# -*- coding: utf-8 -*-

import json

from oauth2client.client import GoogleCredentials
from googleapiclient import discovery

credentials = GoogleCredentials.get_application_default()
ml = discovery.build("ml", "v1beta1", credentials=credentials)

with open("sample.json") as f:
    data = {"instances": [json.loads(i) for i in f]}
req = ml.projects().predict(
    body=data, name="projects/{0}/models/{1}".format("cpb102demo1", "taxifare")
)
result = req.execute()

print result
