# cpo200-authorization

## 同じProjectのCloud Storageに読み書きを行える権限を持ったInstanceを作成

```
gcloud compute instances create auth --zone us-central1-b --scopes storage-full

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/auth].
NAME  ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP     STATUS
auth  us-central1-b  n1-standard-1               10.128.0.2   104.154.241.61  RUNNING
```

[scopeの一覧は `gcloud compute instance create` commandの --scopes を参照](https://cloud.google.com/sdk/gcloud/reference/compute/instances/create)

### Cloud Storageに読み書きできることを確認

```
# ssh接続して、Cloud Storage Default BucketにファイルをUploadする
gcloud compute ssh auth --zone us-central1-b

touch hoge.txt

# ProjectのBucket一覧を確認
gsutil ls
gs://{project-id}.appspot.com/

# ファイルをCloud Storageにコピー
gsutil cp hoge.txt gs://{project-id}.appspot.com/hoge.txt
Copying file://hoge.txt [Content-Type=text/plain]...
/ [1 files][    0.0 B/    0.0 B]
Operation completed over 1 objects.

# Cloud Storageのファイルを削除
gsutil rm gs://{project-id}.appspot.com/hoge.txt
Removing gs://{project-id}.appspot.com/hoge.txt...
/ [1 objects]
Operation completed over 1 objects.
```

[Cloud Storage Default Bucket](http://qiita.com/sinmetal/items/f2f7e0fe444b7e000a61)

## Clean Up

```
gcloud compute instances delete auth --zone us-central1-b

The following instances will be deleted. Attached disks configured to
be auto-deleted will be deleted unless they are attached to any other
instances. Deleting a disk is irreversible and any data on the disk
will be lost.
 - [auth] in [us-central1-b]

Do you want to continue (Y/n)?  Y

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/auth].
```

