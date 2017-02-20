#!/bin/bash

yes | gcloud compute forwarding-rules delete http-rule --global
yes | gcloud compute target-http-proxies delete web-proxy
yes | gcloud compute url-maps delete web-map
yes | gcloud compute backend-services delete web-service
yes | gcloud compute backend-services delete video-service
yes | gcloud compute http-health-checks delete basic-check
yes | gcloud compute instance-groups managed delete "web-group-us-b" --zone "us-central1-b"
yes | gcloud compute instance-groups managed delete "web-group-us-c" --zone "us-central1-c"
yes | gcloud compute instance-groups managed delete "video-group-us-b" --zone "us-central1-b"
yes | gcloud compute instance-groups managed delete "video-group-us-c" --zone "us-central1-c"
yes | gcloud compute instance-templates delete "web-template"
yes | gcloud compute addresses delete lb-ip-cr --global
yes | gcloud compute snapshots delete instance-image-snapshot
yes | gcloud compute disks delete nginx-template --zone us-central1-b
yes | gcloud compute instances delete instance-image --zone us-central1-b
