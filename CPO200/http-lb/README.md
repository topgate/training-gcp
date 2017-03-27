# cpo200-http-lb

## [Compute Engine HTTP LB](https://cloud.google.com/compute/docs/load-balancing/http/) を構築する

![httplb](https://storage.googleapis.com/cpo200demo1.appspot.com/httplb.png "httplb")

### Web Server用のCustom Imageを作成

Installしておくミドルウェア

* nginx
* Cloud Logging Agent
* Cloud Monitoring Agent

#### Cudom Image 用 Instance 作成

```
gcloud compute instances create instance-image --zone us-central1-b
```

ssh接続し、必要なアプリをインストールする

```
gcloud compute ssh --zone "us-central1-b" "instance-image"
```

#### nginx install

```
sudo apt-get update
sudo apt-get install -y nginx
```

#### Cloud Logging Agent install

InstanceのログをCloud Loggingに出力するためにagentをインストールする

[Installing the Logging Agent](https://cloud.google.com/logging/docs/agent/installation)

```
curl -sSO https://dl.google.com/cloudagents/install-logging-agent.sh
sha256sum install-logging-agent.sh
sudo bash install-logging-agent.sh
```

Cloud Logging Agentは [fluentd](http://www.fluentd.org/) Baseで作られている。
fluentdの設定ファイルは `/etc/google-fluentd/config.d` にある。
デフォルトで主要なミドルウェアの設定ファイルのサンプルが置いてあるので、不要なものは削除した方が良い。
nginxも最初から用意されているので、 `/etc/google-fluentd/config.d/nginx.conf` とりあえずログは収集できる。

#### Cloud Monitoring Agent install

Instanceの状態をCloud Monitoringに出力するためのagentをインストールする

[Installing the Monitoring Agent](https://cloud.google.com/monitoring/agent/install-agent)

```
curl -O "https://repo.stackdriver.com/stack-install.sh"
sudo bash stack-install.sh --write-gcm
```

#### sh ファイルの削除

```
rm install-logging-agent.sh
rm stack-install.sh
exit
```

#### Instanceを停止し、Snapshotを作成

```
gcloud compute instances stop instance-image --zone us-central1-b
gcloud compute disks snapshot instance-image --snapshot-names instance-image-snapshot --zone us-central1-b
```

#### SnapshotからDiskを作成し、Custom Imageを作成

```
gcloud compute disks create nginx-template --source-snapshot instance-image-snapshot --zone us-central1-b
gcloud compute images create nginx-image-20161110v1 --family nginx-image --source-disk nginx-template --source-disk-zone us-central1-b
```

### HTTP LBの構築

全コマンドを実行するshell
https://github.com/topgate/cpo200-http-lb/blob/master/create.sh

#### firewall-rule 作成

tcp80を通すfirewall-ruleを作成する

```
gcloud compute firewall-rules create default-allow-http \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server \
    --allow tcp:80
```

#### api用 instance-template 作成

startup-scriptを使って、nginxをinstallするinstance-templateを作成する

```
gcloud compute instance-templates create "web-template" --machine-type "f1-micro" --network "default" --metadata "startup-script-url=gs://cpo200demo1.appspot.com/startup_html.sh" --tags "http-server" --image-family "nginx-image"
```

#### api用 instance-groups 作成 

us-central1-b, us-central1-cにinstance-groupを作成する

```
gcloud compute instance-groups managed create "web-group-us-b" --zone "us-central1-b" --base-instance-name "web-group-us-b" --template "web-template" --size "2"
```

```
gcloud compute instance-groups managed create "web-group-us-c" --zone "us-central1-c" --base-instance-name "web-group-us-b" --template "web-template" --size "2"
```

#### http-health-checks 作成

単純に "/" にリクエストを送るヘルスチェックを作成

```
gcloud compute http-health-checks create basic-check
```

#### api用 backend-service 作成 

/api を配信するbackend-serviceを作成

```
gcloud compute backend-services create web-service --protocol HTTP --http-health-checks basic-check --global
```

#### api用 backend-serviceに、 api用 instance-groupを追加

us-central1-b, us-centra1-cのinstance-groupをbackend-serviceに追加する

```
gcloud compute backend-services add-backend web-service \
    --balancing-mode UTILIZATION \
    --max-utilization 0.8 \
    --capacity-scaler 1 \
    --instance-group web-group-us-b \
    --instance-group-zone us-central1-b \
    --global
```

```
gcloud compute backend-services add-backend web-service \
    --balancing-mode UTILIZATION \
    --max-utilization 0.8 \
    --capacity-scaler 1 \
    --instance-group web-group-us-c \
    --instance-group-zone us-central1-c \
    --global
```

#### video用 instance-template 作成 

中身はnginxなので、特にvideo配信するようにはなってないサンプル

```
gcloud compute instance-templates create "video-template" --machine-type "f1-micro" --network "default" --metadata "startup-script-url=gs://cpo200demo1.appspot.com/startup.sh" --tags "http-server" --image-family "nginx-image"
```

#### video用 instance-group 作成

us-central1-b, us-central1-cにinstance-groupを作成する

```
gcloud compute instance-groups managed create "video-group-us-b" --zone "us-central1-b" --base-instance-name "video-group-us-b" --template "web-template" --size "2"
```

```
gcloud compute instance-groups managed create "video-group-us-c" --zone "us-central1-c" --base-instance-name "video-group-us-b" --template "web-template" --size "2"
```

#### video用 backend-service 作成

```
gcloud compute backend-services create video-service --protocol HTTP --http-health-checks basic-check --global
```

#### video用 backend-serviceに、 video用 instance-groupを追加

```
gcloud compute backend-services add-backend video-service \
    --balancing-mode UTILIZATION \
    --max-utilization 0.8 \
    --capacity-scaler 1 \
    --instance-group video-group-us-b \
    --instance-group-zone us-central1-b \
    --global
```

```
gcloud compute backend-services add-backend video-service \
    --balancing-mode UTILIZATION \
    --max-utilization 0.8 \
    --capacity-scaler 1 \
    --instance-group video-group-us-c \
    --instance-group-zone us-central1-c \
    --global
```

#### url-map 作成

```
gcloud compute url-maps create web-map --default-service web-service
```

#### url-mapに /video,/video/* のpathは、video-serviceに回すように設定

```
gcloud compute url-maps add-path-matcher web-map \
    --default-service web-service \
    --path-matcher-name video-matcher \
    --path-rules "/video=video-service,/video/*=video-service"
```

#### target-http-proxies 作成

```
gcloud compute target-http-proxies create web-proxy --url-map web-map
```

#### global static ip addr 作成

HTTP LBに設定するためのstatic ip addrを作成

```
gcloud compute addresses create lb-ip-cr --global
```

#### forwarding-rule 作成

```
gcloud compute forwarding-rules create http-rule --address {your addr} --global --target-http-proxy web-proxy --ports 80
```

## web-serviceに [Cloud CDN](https://cloud.google.com/cdn/docs/) を設定 (Option)

指定したbackend-serviceのResponseを [エッジキャッシュ](http://qiita.com/sinmetal/items/37c105a098174fb6bf77) に乗せる設定

```
gcloud compute backend-services update web-service --enable-cdn
```

## http-lb helth checkのためのfirewall-rule 作成 (Option)

HTTP(S) LBのヘルスチェックは130.211.0.0/22から来る 
tcp:80を0.0.0.0/0で許可しない場合に設定する

```
gcloud compute firewall-rules create allow-130-211-0-0-22 \
    --source-ranges 130.211.0.0/22 \
    --target-tags http-server \
    --allow tcp:80
```
## CleanUp

[cleanup.sh](https://github.com/topgate/cpo200-http-lb/blob/master/cleanup.sh)

```
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
```
