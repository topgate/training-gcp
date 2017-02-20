#!/bin/bash

gcloud compute instances create www1 www2 www3 --zone "us-central1-a" --tags "http-server" --metadata "startup-script-url=gs://cpo200demo1.appspot.com/startup.sh"

gcloud compute firewall-rules create default-allow-http \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server \
    --allow tcp:80

gcloud compute http-health-checks create basic-check

gcloud compute target-pools create www-pool --region "us-central1" --health-check basic-check

gcloud compute target-pools add-instances www-pool --instances www1,www2,www3 --zone "us-central1-a"

gcloud compute forwarding-rules create www-rule --region "us-central1" --ports 80 --target-pool www-pool



gcloud compute target-pools create reserve-pool --region "us-central1" --health-check basic-check

gcloud compute target-pools set-backup www-pool --backup-pool reserve-pool --failover-ratio 0.4 --region "us-central1"


gcloud compute instances create www4 www5 --zone "us-central1-b" --tags "http-server" --metadata "startup-script-url=gs://cpo200demo1.appspot.com/startup.sh"

gcloud compute target-pools add-instances reserve-pool --instances www4,www5 --zone "us-central1-b"
