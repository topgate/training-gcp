# cpo200-disks

## Imageを指定してInstanceを作成

debian-8のOS Imageを明示的に指定してInstanceを作成します。

### debian image 一覧を確認

debian image一覧をから最新のimage nameを確認する

```
gcloud compute images list --regexp ".*debian.*"
```

### debianの指定したversionのimageでInstanceを作成する

```
gcloud compute instances create sample --image debian-8-jessie-v20170110 --image-project debian-cloud --machine-type g1-small --zone us-central1-b
```

### debianの最新versionのimageでInstanceを作成する

imageはimage-familyでグルーピングされています。 `--image-family` optionを指定した場合、そのimage-familyの中で最新のimageが利用されます。
image-familyのversionが変わるとミドルウェアのversionなども変わる可能性があるため、任意のタイミングでversionを上げたい場合は、imageを明示的に指定した方がよいです。

```
gcloud compute instances create latest-debian-8 --image-family debian-8 --image-project debian-cloud --machine-type g1-small --zone us-central1-b
```

## Diskを追加する

Instanceを作成するとBootDiskが1つある状態となります。
アプリケーションやDBのデータのみを入れたDiskを作りたい場合、新しいDiskを作成してInstanceにattachします。

### Diskを作成

```
gcloud compute disks create additional-disk --size 15 --zone us-central1-b --type pd-ssd

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/disks/additional-disk].
NAME             ZONE           SIZE_GB  TYPE    STATUS
additional-disk  us-central1-b  15       pd-ssd  READY
```

### InstanceにDiskをattach

先程作成したsample instanceにdiskをattachします。 `--device-name` を省略するとOSから見たdiskとResouceとしてのdiskの対応が分からなくなってしまうので、明示的に指定するのがおすすめです。

```
gcloud compute instances attach-disk sample --disk additional-disk --device-name additional-disk --zone us-central1-b
```

### Diskをmountする

diskをattachしただけではOSから認識されていないので、sshで接続してmountを行います。

```
# ssh接続を行う

gcloud compute ssh --zone us-central1-b sample
```

```
# diskはgoogle-{device-name}で認識された状態になります。
# `ls /dev/disk/by-id` で確認してみます。

ls /dev/disk/by-id

google-additional-disk    google-persistent-disk-0-part1               scsi-0Google_PersistentDisk_persistent-disk-0
google-persistent-disk-0  scsi-0Google_PersistentDisk_additional-disk  scsi-0Google_PersistentDisk_persistent-disk-0-part1
```

```
# まだ、mountしてないので、いません

df

Filesystem     1K-blocks   Used Available Use% Mounted on
/dev/sda1       10188088 882592   8764928  10% /
udev               10240      0     10240   0% /dev
tmpfs             349068   4576    344492   2% /run
tmpfs             872664      0    872664   0% /dev/shm
tmpfs               5120      0      5120   0% /run/lock
tmpfs             872664      0    872664   0% /sys/fs/cgroup
```

```
# 新規作成してattachしたdiskはblankの状態なので、formatを行います。

sudo mkfs.ext4 -F -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/disk/by-id/google-additional-disk

mke2fs 1.42.12 (29-Aug-2014)
Discarding device blocks: done
Creating filesystem with 3932160 4k blocks and 983040 inodes
Filesystem UUID: 393d9fa9-9ab0-43ea-a80b-dbb59c01fd0d
Superblock backups stored on blocks:
	32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208

Allocating group tables: done
Writing inode tables: done
Creating journal (32768 blocks): done
Writing superblocks and filesystem accounting information: done
```

```
# mount用のdiskを作成
sudo mkdir -p /mnt/disks/additional-disk
```

```
# mount
sudo mount -o discard,defaults /dev/disk/by-id/google-additional-disk /mnt/disks/additional-disk
```

```
# diskがmountされて、使えるようになりました。

df

Filesystem     1K-blocks   Used Available Use% Mounted on
/dev/sda1       10188088 882620   8764900  10% /
udev               10240      0     10240   0% /dev
tmpfs             349068   4580    344488   2% /run
tmpfs             872664      0    872664   0% /dev/shm
tmpfs               5120      0      5120   0% /run/lock
tmpfs             872664      0    872664   0% /sys/fs/cgroup
/dev/sdb        15350768  38384  14509568   1% /mnt/disks/additional-disk
```

このままではInstanceを再起動した時にmountが外れてしまうので、自動的にmountされるように設定しておきます。

```
echo UUID=`sudo blkid -s UUID -o value /dev/disk/by-id/google-additional-disk` /mnt/disks/additional-disk ext4 discard,defaults,nofail 0 2 | sudo tee -a /etc/fstab
```

## Custom Imageの利用

### Custom Image作成

Custom Imageから作られていることが分かるように、適当にhome diskにファイルを作っておく

```
gcloud compute ssh sample --zone us-central1-b

touch version-1.txt
```

//gcloud compute disks snapshot sample --snapshot-names sample-snapshot --zone us-central1-b
//Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/snapshots/sample-snapshot].

### Diskを残してInstanceを削除する

Custom Imageは、InstanceにattachされていないDiskを元に作られるので、 `sample` のBoot Diskを残した状態で、Instanceを削除します。

```
# sample diskをInstance削除時に一緒に消さないように設定
gcloud compute instances set-disk-auto-delete sample --no-auto-delete --disk sample --zone us-central1-b

Updated [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample].
```

```
# Diskの状態をきれいに保つためにシャットダウンする
gcloud compute instances stop sample --zone us-central1-b

Updated [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample].
```

```
gcloud compute instances delete sample --zone us-central1-b

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample].
```

```
# Diskが残っていることを確認

gcloud compute disks list

NAME             ZONE           SIZE_GB  TYPE         STATUS
additional-disk  us-central1-b  15       pd-ssd       READY
sample           us-central1-b  10       pd-standard  READY
```

### Custom Imageを作成

```
gcloud compute images create sample-image-20160926v1 --family sample-image --source-disk sample --source-disk-zone us-central1-b
Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/images/sample-image-20160926v1].
NAME                     PROJECT      FAMILY        DEPRECATED  STATUS
sample-image-20160926v1  cpo200demo1  sample-image              READY
```

```
# Custom Imageを確認

gcloud compute images list
NAME                                 PROJECT          FAMILY           DEPRECATED  STATUS
sample-image-20160926v1              cpo200demo1      sample-image                 READY
centos-6-v20160921                   centos-cloud     centos-6                     READY
centos-7-v20160921                   centos-cloud     centos-7                     READY
...
```

```
# Custom Imageを利用してInstaceを作成

gcloud compute instances create sample-20160926v1 --image-family sample-image --zone us-central1-b

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample-20160926v1].
NAME               ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP      STATUS
sample-20160926v1  us-central1-b  n1-standard-1               10.128.0.2   104.154.239.117  RUNNING
```

## image-familyの新しいVersionを作成する

image-family `sample-image` に新しいversionのimageを作成してみます

```
# sshで接続してv2用であることが分かるようにファイルを置いておく

gcloud compute ssh sample --zone us-central1-b

touch v2.txt
```

### Boot Diskを残してInstanceを削除

```
# sample-20160926v1 diskをInstance削除時に一緒に消さないように設定
gcloud compute instances set-disk-auto-delete sample-20160926v1 --no-auto-delete --disk sample-20160926v1 --zone us-central1-b                                                                 1 ↵
Updated [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample-20160926v1].
```

```
# sample-20160926v1 instanceを削除

gcloud compute instances delete sample-20160926v1 --zone us-central1-b

The following instances will be deleted. Attached disks configured to
be auto-deleted will be deleted unless they are attached to any other
instances. Deleting a disk is irreversible and any data on the disk
will be lost.
 - [sample-20160926v1] in [us-central1-b]

Do you want to continue (Y/n)?  Y

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample-20160926v1].
```

### Custom Imageを作成

image-family `sample-image` に新しいimageを作成します。
latest versionの判断はimage nameが最も大きいものになるので、YYYYMMDDやversion idを入れて、名前を大きくしていきます。

```
gcloud compute images create sample-image-20160926v2 --family sample-image --source-disk sample-20160926v1 --source-disk-zone us-central1-b

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/images/sample-image-20160926v2].
NAME                     PROJECT      FAMILY        DEPRECATED  STATUS
sample-image-20160926v2  cpo200demo1  sample-image              READY
```

```
# image-family `sample-image` で新たにInstanceを作成

gcloud compute instances create sample-v2 --image-family sample-image --zone us-central1-b
Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample-v2].
NAME       ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP     STATUS
sample-v2  us-central1-b  n1-standard-1               10.128.0.2   104.197.90.222  RUNNING
```

```
# ssh接続して、v2のimageが使われていることを確認

gcloud compute ssh sample-v2
ls

v1.txt  v2.txt
```

image-familyを使えば、imageを利用している側のコードを変えること無く、imageのversion upを行うことができます。

## Clean Up

instanceを削除する

```
gcloud compute instances delete sample-v2 --zone us-central1-b                                                                                                                                 2 ↵
The following instances will be deleted. Attached disks configured to
be auto-deleted will be deleted unless they are attached to any other
instances. Deleting a disk is irreversible and any data on the disk
will be lost.
 - [sample-v2] in [us-central1-b]

Do you want to continue (Y/n)?  Y

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample-v2].
```

imageを削除する

```
gcloud compute images delete sample-image-20160926v1
The following images will be deleted:
 - [sample-image-20160926v1]

Do you want to continue (Y/n)?  Y

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/images/sample-image-20160926v1].
```

```
gcloud compute images delete sample-image-20160926v2
The following images will be deleted:
 - [sample-image-20160926v2]

Do you want to continue (Y/n)?  Y

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/images/sample-image-20160926v2].
```

diskを削除する

```
gcloud compute disks delete additional-disk --zone us-central1-b
The following disks will be deleted. Deleting a disk is irreversible
and any data on the disk will be lost.
 - [additional-disk] in [us-central1-b]

Do you want to continue (Y/n)?  Y

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/disks/additional-disk].
```

```
gcloud compute disks delete sample --zone us-central1-b
The following disks will be deleted. Deleting a disk is irreversible
and any data on the disk will be lost.
 - [sample] in [us-central1-b]

Do you want to continue (Y/n)?  Y

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/disks/sample].
```

```
gcloud compute disks delete sample-20160926v1 --zone us-central1-b
The following disks will be deleted. Deleting a disk is irreversible
and any data on the disk will be lost.
 - [sample-20160926v1] in [us-central1-b]

Do you want to continue (Y/n)?  Y

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/disks/sample-20160926v1].
```
