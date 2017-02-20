# cpo200-instance-groups

## Managed Group

Managed GroupはInstance Templateから指定した数のInstanceを自動で作成するInstance Groupです。
Web Serverをスケールアウトさせるように同じInstnaceを複数作成する時に利用します。

このLabではPreemptivle VMを指定した数起動するInstance Groupを作成します。
Preemptible VMは24h以内に必ずshutdownされますが、Managed Instance Groupを使っている場合、指定したInstance数を維持するように起動状態のPreemptible VMの数を再作成します。

### Instance Templateの作成

Managed Groupを作る場合、Instanceのコピー元となるInstance Templateが必要です。
Instance作成のTemplateとなるので、 `gcloud compute instances create` と同じようなoptionが用意されています。
preemptibleや、machine-type、scopeなどもInstance Templateに設定します。

```
gcloud compute instance-templates create preemptible-vm-template --machine-type f1-micro --no-restart-on-failure --maintenance-policy "TERMINATE" --preemptible

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/instanceTemplates/preemptible-vm-template].
NAME                     MACHINE_TYPE  PREEMPTIBLE  CREATION_TIMESTAMP
preemptible-vm-template  f1-micro      true         2016-09-26T03:51:33.201-07:00
```

### Managed Groupを作成

sizeはInstanceの数です。今回は3を指定しているので、Instanceが3台になるように調整し続けます。

```
gcloud compute instance-groups managed create managed-group --size 3 --template preemptible-vm-template --base-instance-name pre --zone us-central1-b

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instanceGroupManagers/managed-group].
NAME           LOCATION       SCOPE  BASE_INSTANCE_NAME  SIZE  TARGET_SIZE  INSTANCE_TEMPLATE        AUTOSCALED
managed-group  us-central1-b  zone   pre                 0     3            preemptible-vm-template  no
```

#### Instanceの一覧を確認

`--base-instance-name` のoptionに従ってprefixを付けてInstanceが作成されます。

```
gcloud compute instances list

NAME      ZONE           MACHINE_TYPE  PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP      STATUS
pre-6drg  us-central1-b  f1-micro      true         10.128.0.3   104.154.240.255  RUNNING
pre-drn7  us-central1-b  f1-micro      true         10.128.0.2   104.154.40.162   RUNNING
pre-t3d9  us-central1-b  f1-micro      true         10.128.0.4   104.197.247.26   RUNNING
```

### Instance GroupのResize

Instanceの台数をマニュアルで設定し直すことができます。
sizeを0設定することもできます。

```
gcloud compute instance-groups managed resize managed-group --size 0 --zone us-central1-b

Updated [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instanceGroupManagers/managed-group].
---
baseInstanceName: pre
creationTimestamp: '2016-09-26T03:56:43.642-07:00'
currentActions:
  abandoning: 0
  creating: 0
  creatingWithoutRetries: 0
  deleting: 3
  none: 0
  recreating: 0
  refreshing: 0
  restarting: 0
fingerprint: IVlk5PeFAwo=
id: '7073751855381430276'
instanceGroup: managed-group
instanceTemplate: preemptible-vm-template
kind: compute#instanceGroupManager
name: managed-group
selfLink: https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instanceGroupManagers/managed-group
targetSize: 0
zone: us-central1-b
```

#### Instanceの一覧を確認

Instanceがshutdownされたことを確認する。

```
gcloud compute instances list

NAME      ZONE           MACHINE_TYPE  PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP      STATUS
Listed 0 items.
```

### Clean Up

#### instance-groupの削除

```
gcloud compute instance-groups managed delete managed-group --zone us-central1-b

The following instance group managers will be deleted:
 - [managed-group] in [us-central1-b]

Do you want to continue (Y/n)?  Y

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instanceGroupManagers/managed-group].
```

#### instance-templateの削除

```
gcloud compute instance-templates delete preemptible-vm-template
The following instance templates will be deleted:
 - [preemptible-vm-template]

Do you want to continue (Y/n)?  Y

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/instanceTemplates/preemptible-vm-template].
```
