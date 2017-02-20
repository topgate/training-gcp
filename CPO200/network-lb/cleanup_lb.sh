#!/bin/bash

yes | gcloud compute instances delete www1 www2 www3 --zone us-central1-a
yes | gcloud compute instances delete www4 www5 --zone us-central1-b
yes | gcloud compute forwarding-rules delete www-rule --region us-central1
yes | gcloud compute target-pools delete www-pool --region us-central1
yes | gcloud compute target-pools delete reserve-pool --region us-central1
yes | gcloud compute http-health-checks delete basic-check
