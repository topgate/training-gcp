# cpo200-metadata

## Instance Metadata

custom metadata `foo=var` を設定してInstanceを作成

```
gcloud compute instances create sample --metadata foo=var --zone us-central1-b

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample].
NAME    ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP     STATUS
sample  us-central1-b  n1-standard-1               10.128.0.2   104.197.68.192  RUNNING
```

ssh接続を行う

```
gcloud compute ssh sample --zone us-central1-b
```

fooを取得すると、varが返ってくるのを確認

```
curl "http://metadata/computeMetadata/v1/instance/attributes/foo" -H "Metadata-Flavor: Google"

var
```

network-interfacesを確認する。
`recursive=true` をkeyが複数あるときに全て取得するオプション
`alt=text` はResponseの形式をtext形式にするオプション

```
curl "http://metadata/computeMetadata/v1/instance/network-interfaces/0/?recursive=true&alt=text" -H "Metadata-Flavor: Google"

access-configs/0/external-ip 104.199.199.112
access-configs/0/type ONE_TO_ONE_NAT
ip 10.140.0.3
mac 42:01:0a:8c:00:03
network projects/532740595149/networks/default
```

`alt=text` を指定しない場合、デフォルトはjsonで返ってくる

```
curl "http://metadata/computeMetadata/v1/instance/disks/0/?recursive=true" -H "Metadata-Flavor: Google"
{"deviceName":"sample","index":0,"mode":"READ_WRITE","type":"PERSISTENT"}
```

### Service AccountのAccess Tokenを取得

Metadata ServerからService AccountのAccess Tokenを取得できる
自分のプログラムから、Service Accountを使って、APIを叩く時に利用できる

```
curl "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token" \
-H "Metadata-Flavor: Google"

{"access_token":"...","expires_in":3599,"token_type":"Bearer"}
```

### local fileの内容をmetadataのvalurに設定する

metadataのvalueに長い文字列を設定する場合、localfileを読み込んで設定する `--metadata-from-file` が使えます

適当なファイルを作成する

```
echo hoge > meta.txt
```

`meta` keyに `meta.txt` の内容を設定する

```
gcloud compute instances add-metadata sample --metadata-from-file meta=meta.txt --zone us-central1-b

Updated [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample].
```

metadataが設定されたことを確認

```
gcloud compute instances describe sample --zone us-central1-b

canIpForward: false
cpuPlatform: Intel Haswell
creationTimestamp: '2016-09-28T03:06:20.556-07:00'
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
id: '2107503363112708339'
kind: compute#instance
machineType: https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/machineTypes/n1-standard-1
metadata:
  fingerprint: FKBII3VFyVI=
  items:
  - key: foo
    value: var
  - key: meta
    value: |
      hoge
  kind: compute#metadata
name: sample
networkInterfaces:
- accessConfigs:
  - kind: compute#accessConfig
    name: external-nat
    natIP: 104.197.68.192
    type: ONE_TO_ONE_NAT
  name: nic0
  network: https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/networks/default
  networkIP: 10.128.0.2
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
  - https://www.googleapis.com/auth/service.management.readonly
  - https://www.googleapis.com/auth/servicecontrol
status: RUNNING
tags:
  fingerprint: 42WmSpB8rSM=
zone: https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b
```

## Project-wide Metadata

project-wide Metadataに `foo=var` を設定

```
gcloud compute project-info add-metadata --metadata foo=var

Updated [https://www.googleapis.com/compute/v1/projects/cpo200demo1].
```

sshで接続する

```
gcloud compute ssh sample --zone us-central1-b
```

fooを取得すると、varが返ってくるのを確認

```
curl "http://metadata/computeMetadata/v1/project/attributes/foo" -H "Metadata-Flavor: Google"

var
```

ProjectIdが返ってくるのを確認

```
curl "http://metadata/computeMetadata/v1/project/project-id" -H "Metadata-Flavor: Google"

{your project id}
```

最初から用意されている [metadata 一覧](https://cloud.google.com/compute/docs/storing-retrieving-metadata#default)

## Clean Up

Instanceを削除

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

Project-wide Metadataを削除

```
gcloud compute project-info remove-metadata --keys foo

Updated [https://www.googleapis.com/compute/v1/projects/cpo200demo1].
```
