# cpo200-instance-groups

## Unmanaged Group

Unmanaged Groupは、既存のInstanceのグルーピングを行う機能です。
LBの宛先として、手動で作成した複数のInstanceを扱いたい時などに利用します。

### Unmanaged Groupを作成

```
gcloud compute instance-groups unmanaged create unmanaged-group --zone us-central1-b

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instanceGroups/unmanaged-group].
NAME             LOCATION       SCOPE  NETWORK  MANAGED  INSTANCES
unmanaged-group  us-central1-b  zone                     0
```

### Unmanaged Groupに入れるためのInstanceを作成

```
gcloud compute instances create sample1 --zone us-central1-b

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample1].
NAME     ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP    STATUS
sample1  us-central1-b  n1-standard-1               10.128.0.2   23.236.49.232  RUNNING
```

### Unmanaged GroupにInstanceを追加

```
gcloud compute instance-groups unmanaged add-instances unmanaged-group --instances sample1 --zone us-central1-b

Updated [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instanceGroups/unmanaged-group].
```

### Unmanaged Groupに所属しているInstance一覧を取得

```
gcloud compute instance-groups unmanaged list-instances unmanaged-group --zone us-central1-b

NAME     STATUS
sample1  RUNNING
```

### Unmanaged Groupにもう1つInstanceを追加する

```
gcloud compute instances create sample2 --zone us-central1-b

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample2].
NAME     ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP      STATUS
sample2  us-central1-b  n1-standard-1               10.128.0.3   104.155.172.204  RUNNING
```

```
gcloud compute instance-groups unmanaged add-instances unmanaged-group --instances sample2 --zone us-central1-b

Updated [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instanceGroups/unmanaged-group].
```

### Unmanaged GroupのInstanceが2つになったことを確認

```
gcloud compute instance-groups unmanaged list-instances unmanaged-group --zone us-central1-b

NAME     STATUS
sample1  RUNNING
sample2  RUNNING
```

### Unmanaged GroupからInstanceを削除

```
gcloud compute instance-groups unmanaged remove-instances unmanaged-group --instances sample1 --zone us-central1-b

Updated [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instanceGroups/unmanaged-group].
```

### Unmanaged GroupのInstance1つになったことを確認

```
gcloud compute instance-groups unmanaged list-instances unmanaged-group --zone us-central1-b

NAME     STATUS
sample2  RUNNING
```

## Clean Up

### instance-groups 削除

```
gcloud compute instance-groups unmanaged delete unmanaged-group --zone us-central1-b

The following instance groups will be deleted:
 - [unmanaged-group] in [us-central1-b]

Do you want to continue (Y/n)?  Y

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instanceGroups/unmanaged-group].
```

### Instanceを削除

```
gcloud compute instances delete sample1 --zone us-central1-b

The following instances will be deleted. Attached disks configured to
be auto-deleted will be deleted unless they are attached to any other
instances. Deleting a disk is irreversible and any data on the disk
will be lost.
 - [sample1] in [us-central1-b]

Do you want to continue (Y/n)?  Y

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample1].
```

```
gcloud compute instances delete sample2 --zone us-central1-b
The following instances will be deleted. Attached disks configured to
be auto-deleted will be deleted unless they are attached to any other
instances. Deleting a disk is irreversible and any data on the disk
will be lost.
 - [sample2] in [us-central1-b]

Do you want to continue (Y/n)?  Y

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample2].
```
