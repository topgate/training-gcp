#!/bin/bash

gcloud compute firewall-rules create default-allow-http \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server \
    --allow tcp:80

gcloud compute instance-templates create "web-template" --machine-type "f1-micro" --network "default" --metadata "startup-script-url=gs://cpo200demo1.appspot.com/startup_html.sh" --tags "http-server" --image-family "nginx-image"

gcloud compute instance-groups managed create "web-group-us-b" --zone "us-central1-b" --base-instance-name "web-group-us-b" --template "web-template" --size "2"
gcloud compute instance-groups managed create "web-group-us-c" --zone "us-central1-c" --base-instance-name "web-group-us-b" --template "web-template" --size "2"

gcloud compute http-health-checks create basic-check

gcloud compute backend-services create web-service --protocol HTTP --http-health-checks basic-check

gcloud compute backend-services add-backend web-service \
    --balancing-mode UTILIZATION \
    --max-utilization 0.8 \
    --capacity-scaler 1 \
    --instance-group web-group-us-b \
    --instance-group-zone us-central1-b

gcloud compute backend-services add-backend web-service \
    --balancing-mode UTILIZATION \
    --max-utilization 0.8 \
    --capacity-scaler 1 \
    --instance-group web-group-us-c \
    --instance-group-zone us-central1-c

gcloud compute instance-templates create "video-template" --machine-type "f1-micro" --network "default" --metadata "startup-script-url=gs://cpo200demo1.appspot.com/startup.sh" --tags "http-server" --image "/debian-cloud/debian-8-jessie-v20161027"

gcloud compute instance-groups managed create "video-group-us-b" --zone "us-central1-b" --base-instance-name "video-group-us-b" --template "web-template" --size "2"
gcloud compute instance-groups managed create "video-group-us-c" --zone "us-central1-c" --base-instance-name "video-group-us-b" --template "web-template" --size "2"

gcloud compute backend-services create video-service --protocol HTTP --http-health-checks basic-check

gcloud compute backend-services add-backend video-service \
    --balancing-mode UTILIZATION \
    --max-utilization 0.8 \
    --capacity-scaler 1 \
    --instance-group video-group-us-b \
    --instance-group-zone us-central1-b

gcloud compute backend-services add-backend video-service \
    --balancing-mode UTILIZATION \
    --max-utilization 0.8 \
    --capacity-scaler 1 \
    --instance-group video-group-us-c \
    --instance-group-zone us-central1-c

gcloud compute url-maps create web-map --default-service web-service

gcloud compute url-maps add-path-matcher web-map \
    --default-service web-service \
    --path-matcher-name video-matcher \
    --path-rules "/video=video-service,/video/*=video-service"

gcloud compute target-http-proxies create web-proxy --url-map web-map

gcloud compute backend-services update web-service --enable-cdn
