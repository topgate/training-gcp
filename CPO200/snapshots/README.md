# cpo200-snapshots

snapshotはPersistent DiskのBackupや、disk-type, zone の変更などに利用する
Persistent Diskは作成サイズが課金対象だが、SnapshotはPersistent Diskの実際に使われている容量のみ作成されるので、使わないPersistent DiskはSnapshotを作って、Diskを削除した方がお得

## snapshotを使って、disk typeを変えつつ、別zoneにコピーする

instanceを作成

```
gcloud compute instances create sample --zone us-central1-b
Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample].
NAME    ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP     STATUS
sample  us-central1-b  n1-standard-1               10.128.0.2   104.197.207.41  RUNNING
```

diskを確認

```
gcloud compute disks list

NAME    ZONE           SIZE_GB  TYPE         STATUS
sample  us-central1-b  10       pd-standard  READY
```

snapshotを作成する

```
gcloud compute disks snapshot sample --snapshot-names snapshot-sample --zone us-central1-b
Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/snapshots/snapshot-sample].
```

typeをssdにし、zoneをasia-east1-bにして、snapshotからdiskを作成

```
gcloud compute disks create sample --source-snapshot snapshot-sample --type pd-ssd --zone asia-east1-b

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/asia-east1-b/disks/sample].
NAME    ZONE          SIZE_GB  TYPE    STATUS
sample  asia-east1-b  10       pd-ssd  READY

New disks are unformatted. You must format and mount a disk before it
can be used. You can find instructions on how to do this at:

https://cloud.google.com/compute/docs/disks/add-persistent-disk#formatting
```

standard diskをssdに変換して、zoneをasia-east1-bにできたことを確認

```
gcloud compute disks list

NAME    ZONE           SIZE_GB  TYPE         STATUS
sample  asia-east1-b   10       pd-ssd       READY
sample  us-central1-b  10       pd-standard  READY
```

## 差分 snapshot

同じdiskから複数回snapshotを作成した場合、2回目からは差分のみが作成される
毎日snapshotを作成した場合、差分のみが作られるので、料金がお安くなる

```
gcloud compute disks snapshot sample --snapshot-names snapshot-sample2 --zone us-central1-b

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/snapshots/snapshot-sample2].
```

snapshotのdisk sizeは `gcloud compute snapshots list` では返ってこないので、Developers Consonleで確認
[snapshot](https://console.cloud.google.com/compute/snapshots)

`snapshot-sample2` は `snapshot-sample` より小さいサイズになる

同じDiskから作られたという判断は `sourceDiskId` で行っている
sourceDiskIdをDiskを一意に識別するために自動的に割り振られている

```
gcloud compute snapshots describe snapshot-sample

creationTimestamp: '2016-09-25T21:18:14.144-07:00'
diskSizeGb: '10'
id: '1267795733000822633'
kind: compute#snapshot
licenses:
- https://www.googleapis.com/compute/v1/projects/debian-cloud/global/licenses/debian-8-jessie
name: snapshot-sample
selfLink: https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/snapshots/snapshot-sample
sourceDisk: https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/disks/sample
sourceDiskId: '4364002949056510461'
status: READY
storageBytes: '541715442'
storageBytesStatus: UP_TO_DATE
```

差分 snapshotの古いversionを削除すると、その1つ前のversionにmergeされる
試しに `snapshot-sample` を削除して、 `snapshot-sample2` のサイズがどうなるのかを確認する

```
gcloud compute snapshots delete snapshot-sample

The following snapshots will be deleted:
 - [snapshot-sample]

Do you want to continue (Y/n)?  Y

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/snapshots/snapshot-sample].
```

`snapshot-sample2` のサイズをDevelopers Consonleで確認
[snapshot](https://console.cloud.google.com/compute/snapshots)

## Clean Up

snapshotを削除

```
gcloud compute snapshots delete snapshot-sample

The following snapshots will be deleted:
 - [snapshot-sample]

Do you want to continue (Y/n)?  Y

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/snapshots/snapshot-sample].
```

snapshotを削除

```
gcloud compute snapshots delete snapshot-sample2

The following snapshots will be deleted:
 - [snapshot-sample2]

Do you want to continue (Y/n)?  Y

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/snapshots/snapshot-sample2].
```

diskを削除

```
gcloud compute disks delete sample --zone asia-east1-b

The following disks will be deleted. Deleting a disk is irreversible
and any data on the disk will be lost.
 - [sample] in [asia-east1-b]

Do you want to continue (Y/n)?  Y

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/asia-east1-b/disks/sample].
```

instanceを削除

```
gcloud compute instances delete sample --zone us-central1-b

The following instances will be deleted. Attached disks configured to
be auto-deleted will be deleted unless they are attached to any other
instances. Deleting a disk is irreversible and any data on the disk
will be lost.
 - [sample] in [us-central1-b]

Do you want to continue (Y/n)?  Y

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample].
```
