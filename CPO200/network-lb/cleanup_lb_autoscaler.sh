#!/bin/bash

yes | gcloud compute forwarding-rules delete www-rule --region us-central1
yes | gcloud compute instance-groups managed delete www-instance-group --zone us-central1-b
yes | gcloud compute target-pools delete www-pool --region "us-central1"
yes | gcloud compute http-health-checks delete basic-check
yes | gcloud compute instance-templates delete www-template
