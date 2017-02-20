#!/bin/bash

gcloud compute instance-templates create www-template --tags http-server,https-server --metadata "startup-script-url=gs://cpo200demo1.appspot.com/startup.sh"

gcloud compute http-health-checks create basic-check

gcloud compute target-pools create www-pool --region "us-central1" --health-check basic-check

gcloud compute instance-groups managed create www-instance-group \
  --zone us-central1-b \
  --base-instance-name www \
  --size 1 \
  --template www-template \
  --target-pool www-pool

gcloud compute instance-groups managed resize www-instance-group \
  --zone us-central1-b \
   --size 3

gcloud compute instance-groups managed set-autoscaling www-instance-group \
  --max-num-replicas 5 \
  --min-num-replicas 1 \
  --target-cpu-utilization 0.02 \
  --zone us-central1-b

 gcloud compute forwarding-rules create www-rule --region "us-central1" --port-range 80 --target-pool www-pool
