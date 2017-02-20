# cpo200-startup-script

## Startup Script

Instance起動時に、nginxをインストールして動かす

### localにあるshをStartup Scriptとして設定

nginxをinstallする簡単な `startup.sh` を作成する

```
sudo apt-get update
sudo apt-get install -y nginx
echo "My host name is $HOSTNAME." | sudo tee /var/www/html/index.nginx-debian.html
```

metadata `startup-script` keyに、 `startup.sh` の中身を入れる

```
gcloud compute instances create sample --zone us-central1-b --metadata-from-file startup-script=startup.sh --tags http-server

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample].
NAME    ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP     STATUS
sample  us-central1-b  n1-standard-1               10.128.0.2   104.197.68.192  RUNNING
```

ExternalIPにアクセスして、 `My host name is sample.` と表示されることを確認

### Cloud StorageにあるファイルをStartups Scriptとして利用する

Cloud StorageにshをUpload

```
gsutil cp startup.sh gs://{your bucket}/startup.sh

Copying file://startup.sh [Content-Type=application/x-sh]...
/ [1 files][  132.0 B/  132.0 B]
Operation completed over 1 objects/132.0 B.
```

`startup-script-url` に Cloud StorageのPathを設定して、Instanceを作成

```
gcloud compute instances create sample2 --zone us-central1-b --metadata startup-script-url=gs://{your bucket}/startup.sh --tags http-server

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample2].
NAME     ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP    STATUS
sample2  us-central1-b  n1-standard-1               10.128.0.4   104.197.83.88  RUNNING
```

ExternalIPにアクセスして、 `My host name is sample2.` と表示されることを確認


## Shutdown Script

死ぬときに、Cloud Storageに遺言を残す

###  localにあるshをShutdown Scriptとして設定

Cloud Storageに遺言を残す `shutdown.sh` を作成する

```
echo $HOSTNAME | gsutil cp - gs://{your bucket}/$HOSTNAME
```

metadata `shutdown-script` keyに、 `shutdown.sh` の中身を入れる

```
gcloud compute instances create sample3 --zone us-central1-b --metadata-from-file shutdown-script=shutdown.sh --scopes "https://www.googleapis.com/auth/devstorage.read_write"

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample3].
NAME     ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP     STATUS
sample3  us-central1-b  n1-standard-1               10.128.0.3   104.155.138.44  RUNNING
```

sample3を停止する

```
gcloud compute instances stop sample3 --zone us-central1-b

Updated [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample3].
```

Cloud Storageに遺言が残っていることを確認

```
gsutil ls gs://{your bucket}
```

## Clean Up

Instance 削除

```
gcloud compute instances delete sample sample2 sample3 --zone us-central1-b
```

Cloud Storageのファイルを削除

```
gsutil -m rm "gs://{your bucket}/*"
```
