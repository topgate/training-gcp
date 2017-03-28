# cpo200-network-lb

## [Compute Engine Network LB](https://cloud.google.com/compute/docs/load-balancing/network/) を構築する

![networklb](https://storage.googleapis.com/cpo200demo1.appspot.com/networklb.png "networklb")

### default pool 構築

#### default pool用 instance 作成

```
gcloud compute instances create www1 www2 www3 --zone "us-central1-a" --tags "http-server" --metadata "startup-script-url=gs://cpo200demo1.appspot.com/startup.sh"
```

#### firewall-rule 作成

```
gcloud compute firewall-rules create default-allow-http \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server \
    --allow tcp:80
```

#### http-health-check 作成

"/" にリエクストを送るシンプルなもの

```
gcloud compute http-health-checks create basic-check
```

#### default target-pool 作成

```
gcloud compute target-pools create www-pool --region "us-central1" --health-check basic-check
```

#### default target-poolにinstanceを追加

```
gcloud compute target-pools add-instances www-pool --instances www1,www2,www3 --zone "us-central1-a"
```

#### forwarding-rule 作成

LBの本体のようなもの。
これでひとまず完成。

```
gcloud compute forwarding-rules create www-rule --region "us-central1" --ports 80 --target-pool www-pool
```

### backup-pool 構築

#### backup-pool 用 target-pool 作成

```
gcloud compute target-pools create reserve-pool --region "us-central1" --health-check basic-check
```

#### backup-pool 設定

default poolの生存率が40%を切ったら、backup-poolに切り替わるように設定

```
gcloud compute target-pools set-backup www-pool --backup-pool reserve-pool --failover-ratio 0.4 --region "us-central1"
```

#### backup-pool用 instance 作成

```
gcloud compute instances create www4 www5 --zone "us-central1-b" --tags "http-server" --metadata "startup-script-url=gs://cpo200demo1.appspot.com/startup.sh"
```

#### backup-poolにinstanceを追加

```
gcloud compute target-pools add-instances reserve-pool --instances www4,www5 --zone "us-central1-b"
```

### CleanUp

```
yes | gcloud compute instances delete www1 www2 www3 --zone us-central1-a
yes | gcloud compute instances delete www4 www5 --zone us-central1-b
yes | gcloud compute forwarding-rules delete www-rule --region us-central1
yes | gcloud compute target-pools delete www-pool --region us-central1
yes | gcloud compute target-pools delete reserve-pool --region us-central1
yes | gcloud compute http-health-checks delete basic-check
```

## Network LB with Autoscaler

![networklb_autoscaler1](https://storage.googleapis.com/cpo200demo1.appspot.com/networklb_autoscaler1.png "networklb_autoscaler1")

#### instance template 作成

```
gcloud compute instance-templates create www-template --tags http-server,https-server --metadata "startup-script-url=gs://cpo200demo1.appspot.com/startup.sh"
```

#### http-health-check 作成

"/" にリエクストを送るシンプルなもの

```
gcloud compute http-health-checks create basic-check
```

#### target-pool 作成

```
gcloud compute target-pools create www-pool --region "us-central1" --health-check basic-check
```

#### managed instance group 作成

instance groupをtarget-poolの中に入れるようにする

```
gcloud compute instance-groups managed create www-instance-group \
  --zone us-central1-b \
  --base-instance-name www \
  --size 1 \
  --template www-template \
  --target-pool www-pool
```

#### instnace groupをresizeする

```
gcloud compute instance-groups managed resize www-instance-group \
  --zone us-central1-b \
   --size 3
```

#### autoscalerを設定

1台~5台の間で、CPU利用率が2%を超えたら増やす

```
gcloud compute instance-groups managed set-autoscaling www-instance-group \
  --max-num-replicas 5 \
  --min-num-replicas 1 \
  --target-cpu-utilization 0.02 \
  --zone us-central1-b
```

#### fowarding-rule 作成

```
gcloud compute forwarding-rules create www-rule --region "us-central1" --port-range 80 --target-pool www-pool
```

### Caution

* autoscalerはtarget poolの生存率にも影響を与えるので、backup poolとは相性が悪い
* zoneのフェイルオーバーを考える場合は、instance groupを複数作る

[resource](https://cloud.google.com/compute/docs/autoscaler/scaling-cpu-load-balancing#scale_based_on_network_load_balancing)

#### zoneのフェイルオーバーを考慮して、複数のinstance groupを利用している図

![networklb_autoscaler2](https://storage.googleapis.com/cpo200demo1.appspot.com/networklb_autoscaler2.png "networklb_autoscaler2")

## Resources

* [オートスケーラーの判断についての理解](https://cloud.google.com/compute/docs/autoscaler/understanding-autoscaler-decisions)
* [異常なインスタンスの取り扱い](https://cloud.google.com/compute/docs/load-balancing/health-checks#handling_unhealthy_instances)
## CleanUp

```
yes | gcloud compute forwarding-rules delete www-rule --region us-central1
yes | gcloud compute instance-groups managed delete www-instance-group --zone us-central1-b
yes | gcloud compute target-pools delete www-pool --region "us-central1"
yes | gcloud compute http-health-checks delete basic-check
yes | gcloud compute instance-templates delete www-template
```
