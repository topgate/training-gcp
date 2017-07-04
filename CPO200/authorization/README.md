# cpo200-authorization

## Cloud Storageに読み書きを行える権限を持ったInstanceを作成

```
gcloud compute instances create auth --zone us-central1-b --scopes storage-full

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/auth].
NAME  ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP     STATUS
auth  us-central1-b  n1-standard-1               10.128.0.2   104.154.241.61  RUNNING
```

[scopeの一覧は `gcloud compute instance create` commandの --scopes を参照](https://cloud.google.com/sdk/gcloud/reference/compute/instances/create)

### Cloud Storageに読み書きできることを確認

#### Cloud Storageに作業用bucketを作成

```
# Cloud ShellからProjectIDと同じ名前のbucketを作成する
gsutil mb gs://$DEVSHELL_PROJECT_ID
```

#### Compute EngineからCloud Storageへ読み書きを行う

```
# ssh接続を行う
gcloud compute ssh auth --zone us-central1-b

# accountがService Accountになっていることを確認する
gcloud config list

[core]
account = {project number}-compute@developer.gserviceaccount.com
disable_usage_reporting = True
project = cpo200demo1

# Cloud StorageにUploadするファイルを作成
touch hoge.txt

# ProjectのBucket一覧を確認
gsutil ls

# ファイルをCloud Storageにコピー
gsutil cp hoge.txt gs://{project-id}/hoge.txt
Copying file://hoge.txt [Content-Type=text/plain]...
/ [1 files][    0.0 B/    0.0 B]
Operation completed over 1 objects.

# Cloud Storageのファイルを削除
gsutil rm gs://{project-id}/hoge.txt
Removing gs://{project-id}/hoge.txt...
/ [1 objects]
Operation completed over 1 objects.
```

## Clean Up

```
gcloud compute instances delete auth --zone us-central1-b

gsutil rb gs://$DEVSHELL_PROJECT_ID
```

## 別ProjectのResourceを操作できるようにIAMの設定を行う

### GCP Projectの作成
https://github.com/topgate/training-gcp/tree/master/CPO200/projects を参考にもう1つGCP Projectを作成する
ここで作成したProjectを以下ではOther Projectと呼ぶ

### IAM設定
Compute EngineのService AccountがOther ProjectをOther ProjectのIAMにProject Viewerとして追加する

![IAM設定スクリーンショット](https://github.com/topgate/training-gcp/blob/master/CPO200/authorization/IAM_-_cpo200demo1-dev.png "IAM設定スクリーンショット")

## Other Projectにあとで確認するためのInstanceを作成

```
gcloud compute instances create sample --zone us-central1-b

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1-dev/zones/us-central1-b/instances/auth].
NAME    ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP     STATUS
sample  us-central1-b  n1-standard-1               10.128.0.2   104.154.241.61  RUNNING
```

### Compute Engineの読み込みを行える権限を持ったInstanceをDefault Projectに作成

```
gcloud compute instances create auth --zone us-central1-b --scopes https://www.googleapis.com/auth/compute.readonly

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/auth].
NAME  ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP     STATUS
auth  us-central1-b  n1-standard-1               10.128.0.2   104.154.241.61  RUNNING
```

### Compute Engineの読み込みができることを確認

```
# ssh接続を行う
gcloud compute ssh auth --zone us-central1-b

# accountがService Accountになっていることを確認する
gcloud config list

[core]
account = {project number}-compute@developer.gserviceaccount.com
disable_usage_reporting = True
project = cpo200demo1

# Other ProjectのCompute EngineのInstance Resourceを確認する
gcloud compute instances list --project {other project id}

NAME    ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP     STATUS
sample  us-central1-b  n1-standard-1               10.128.0.2   104.154.241.61  RUNNING
```

## Clean Up

### Default Project

```
gcloud compute instances delete auth --zone us-central1-b
```

### Other Project

```
gcloud compute instances delete sample --zone us-central1-b
```
