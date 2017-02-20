# cpo200-instances

## Instanceを作成する

Compute EngineのInstanceを作成します。
まずはシンプルにデフォルトの状態でInstanceを生成します。

```
gcloud compute instances create sample --zone us-central1-b

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample].
NAME    ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP    STATUS
sample  us-central1-b  n1-standard-1               10.128.0.3   146.148.96.60  RUNNING
```

InstanceはZoneに紐づくResourceなので、どこのZoneに作成するのかのOptionは必須です。
作成されたInstanceの詳細情報を確認します。
デフォルトではImageはDebianが選択され、Boot Diskとして、Standard Disk 10GBが割り当てられます。

```
gcloud compute instances describe sample --zone us-central1-b

canIpForward: false
cpuPlatform: Intel Haswell
creationTimestamp: '2016-09-19T19:31:50.009-07:00'
disks:
- autoDelete: true
  boot: true
  deviceName: persistent-disk-0
  index: 0
  interface: SCSI
  kind: compute#attachedDisk
  licenses:
  - https://www.googleapis.com/compute/v1/projects/debian-cloud/global/licenses/debian-8-jessie
  mode: READ_WRITE
  source: https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/disks/sample
  type: PERSISTENT
id: '7215165088121823609'
kind: compute#instance
machineType: https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/machineTypes/n1-standard-1
metadata:
  fingerprint: -VPfCs9mMp4=
  kind: compute#metadata
name: sample
networkInterfaces:
- accessConfigs:
  - kind: compute#accessConfig
    name: external-nat
    natIP: 146.148.96.60
    type: ONE_TO_ONE_NAT
  name: nic0
  network: https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/networks/default
  networkIP: 10.128.0.3
  subnetwork: https://www.googleapis.com/compute/v1/projects/cpo200demo1/regions/us-central1/subnetworks/default
scheduling:
  automaticRestart: true
  onHostMaintenance: MIGRATE
  preemptible: false
selfLink: https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample
serviceAccounts:
- email: 532740595149-compute@developer.gserviceaccount.com
  scopes:
  - https://www.googleapis.com/auth/cloud.useraccounts.readonly
  - https://www.googleapis.com/auth/devstorage.read_only
  - https://www.googleapis.com/auth/logging.write
  - https://www.googleapis.com/auth/monitoring.write
  - https://www.googleapis.com/auth/service.management
  - https://www.googleapis.com/auth/servicecontrol
status: RUNNING
tags:
  fingerprint: 42WmSpB8rSM=
zone: https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b
```

## Instance一覧の確認

ProjectのInstance一覧を確認します。

```
gcloud compute instances list

NAME       ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP    STATUS
lamp-1-vm  us-central1-b  f1-micro       true         10.128.0.2                  TERMINATED
sample     us-central1-b  n1-standard-1               10.128.0.3   146.148.96.60  RUNNING
```

## InstanceにSSHで接続する

Compute Engineは、SSHのKeyを自動で登録して接続する機能を持っています。
そのため、Instance作成後に、何の設定もしなくても、すぐにSSH接続できます。
SSHできるユーザはProjectのRoleを持っているメンバーです。

### gcloud compute sshで接続できるRole

* Project Owner
* Project Editor
* compute.instanceAdmin
* iam.serviceAccountActor

```
gcloud compute ssh --zone us-central1-b sample
```

ユーザはgcloud compute sshを実行したユーザ名と同じになります。
任意のユーザ名を使う場合は、以下のようにします。

```
gcloud compute ssh --zone us-central1-b hoge@sample
```

## Quotaの確認

Compute EngineはRegionごとに作成できるResourceに制限があります。
上限と利用している数を知るためにはRegionの一覧を確認します。

```
gcloud compute regions list
NAME          CPUS    DISKS_GB    ADDRESSES  RESERVED_ADDRESSES  STATUS  TURNDOWN_DATE
asia-east1    0/2400  0/1000000   0/2300     0/700               UP
europe-west1  0/2400  0/1000000   0/2300     0/700               UP
us-central1   1/2400  20/1000000  1/2300     0/700               UP
us-east1      0/2400  0/1000000   0/2300     0/700               UP
us-west1      0/2400  0/1000000   0/2300     0/700               UP
```

Quotaは [Developers Console](https://console.cloud.google.com/compute/quotas)からでも確認できます。
Quotaは変更することも可能です。Instanceが誤って作られすぎないように小さくしたり、足りない場合は増やすこともできます。
[Developers Console](https://console.cloud.google.com/compute/quotas) の `Request increase` or `増加をリクエスト` からリクエストを送りましょう。
Quotaの変更には時間がかかるケースもあるため、早めに申請した方がよいです。
特にDevelopのProjectのQuotaを上げたが、ProductionのProjectのQuotaを上げ忘れていたパターンがあるため、Developを上げた場合はProductionも合わせて上げておくとよいです。

## Clean Up

Instanceが動いている状態だと1minごとに料金がかかるため、必要なくなったら削除します。
デフォルトではInstanceを削除するとBoot Diskも一緒に削除されるようになっています。

```
gcloud compute instances delete sample --zone us-central1-b
```

Instanceが無くなったことを確認します。

```
gcloud compute instances list

NAME       ZONE           MACHINE_TYPE  PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP  STATUS
```
