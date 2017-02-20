# cpo200-networks

## network関係のResouceのデフォルトの状態を確認する

### network 一覧を確認

`default` という名前のnetworkが用意されています。
Instanceを作成する時に、どのnetworkに所属するかを選択することができます。
デフォルトでは `default` に所属します。

```
gcloud compute networks list

NAME     MODE  IPV4_RANGE  GATEWAY_IPV4
default  auto
```

### subnetwork 一覧を確認

`default` networkの中にsubnetworkがRegionごとに存在します。

```
gcloud compute networks subnets list

NAME     REGION        NETWORK  RANGE
default  asia-east1    default  10.140.0.0/20
default  us-west1      default  10.138.0.0/20
default  us-central1   default  10.128.0.0/20
default  europe-west1  default  10.132.0.0/20
default  us-east1      default  10.142.0.0/20
```

### firewall-rule一覧を確認

一般的に利用しそうなPortが最初から開けてあります。
ただ、セキュリティ的には甘めの設定になっているため、Production環境では厳しく設定し直すことになります。

```
gcloud compute firewall-rules list

NAME                    NETWORK  SRC_RANGES    RULES                         SRC_TAGS  TARGET_TAGS
default-allow-http      default  0.0.0.0/0     tcp:80                                  http-server
default-allow-https     default  0.0.0.0/0     tcp:443                                 https-server
default-allow-icmp      default  0.0.0.0/0     icmp
default-allow-internal  default  10.128.0.0/9  tcp:0-65535,udp:0-65535,icmp
default-allow-rdp       default  0.0.0.0/0     tcp:3389
default-allow-ssh       default  0.0.0.0/0     tcp:22
```

### route一覧を確認

routeは通信時のNextHopを指定することができる機能です。
デフォルトでは、Internet Gatewayが設定されてます。

```
gcloud compute routes list

NAME                            NETWORK  DEST_RANGE     NEXT_HOP                  PRIORITY
default-route-4432c2a0bfc4cff8  default  10.140.0.0/20                            1000
default-route-69d3ff16b34344e0  default  10.138.0.0/20                            1000
default-route-6d5b07e970653398  default  0.0.0.0/0      default-internet-gateway  1000
default-route-7bac35a003cac706  default  10.132.0.0/20                            1000
default-route-95f1875ad87448e0  default  10.142.0.0/20                            1000
default-route-cf5f1cdd8aa93aa3  default  10.128.0.0/20                            1000
```

## 新しいnetworkを作成

networkのデフォルトの状態を確認するために、新しいnetworkを作ってみましょう。

```
gcloud compute networks create sample-net --mode custom

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/networks/sample-net].
NAME        MODE    IPV4_RANGE  GATEWAY_IPV4
sample-net  custom

Instances on this network will not be reachable until firewall rules
are created. As an example, you can allow all internal traffic between
instances as well as SSH, RDP, and ICMP by running:

$ gcloud compute firewall-rules create <FIREWALL_NAME> --network sample-net --allow tcp,udp,icmp --source-ranges <IP_RANGE>
$ gcloud compute firewall-rules create <FIREWALL_NAME> --network sample-net --allow tcp:22,tcp:3389,icmp
```

### 作成したnetworkの詳細情報を確認

```
gcloud compute networks describe sample-net

autoCreateSubnetworks: false
creationTimestamp: '2016-09-19T20:37:39.886-07:00'
id: '123970634119975404'
kind: compute#network
name: sample-net
selfLink: https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/networks/sample-net
x_gcloud_mode: custom
```

### 作成したnetworkにsubnetを作成

subnetはRegion単位のため、作成時にRegionを指定する。

```
gcloud compute networks subnets \                                                                                           
create build-subnet \
--network sample-net \
--region us-central1 \
--range 192.168.5.0/24

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/regions/us-central1/subnetworks/build-subnet].
NAME          REGION       NETWORK     RANGE
build-subnet  us-central1  sample-net  192.168.5.0/24
```

新しくnetowrkを作った場合、firewall-ruleはデフォルトでは何も設定されません。
そのため、このnetworkにInstanceを入れた場合、何のプロトコルを使っても接続できません。

```
gcloud compute firewall-rules list

NAME                    NETWORK  SRC_RANGES    RULES                         SRC_TAGS  TARGET_TAGS
default-allow-http      default  0.0.0.0/0     tcp:80                                  http-server
default-allow-https     default  0.0.0.0/0     tcp:443                                 https-server
default-allow-icmp      default  0.0.0.0/0     icmp
default-allow-internal  default  10.128.0.0/9  tcp:0-65535,udp:0-65535,icmp
default-allow-rdp       default  0.0.0.0/0     tcp:3389
default-allow-ssh       default  0.0.0.0/0     tcp:22
```

```
gcloud compute routes list
NAME                            NETWORK     DEST_RANGE      NEXT_HOP                  PRIORITY
default-route-4432c2a0bfc4cff8  default     10.140.0.0/20                             1000
default-route-69d3ff16b34344e0  default     10.138.0.0/20                             1000
default-route-6d5b07e970653398  default     0.0.0.0/0       default-internet-gateway  1000
default-route-79c0046dcf71a84b  sample-net  192.168.5.0/24                            1000
default-route-7bac35a003cac706  default     10.132.0.0/20                             1000
default-route-95f1875ad87448e0  default     10.142.0.0/20                             1000
default-route-cf5f1cdd8aa93aa3  default     10.128.0.0/20                             1000
default-route-dcc837dbdfedccc0  sample-net  0.0.0.0/0       default-internet-gateway  1000
```

### Instanceを新しいnetworkに入れる

build-subnet を設定したInstanceを新しく作成します。

```
gcloud compute instances create sample --zone us-central1-b --subnet build-subnet

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample].
NAME    ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP     STATUS
sample  us-central1-b  n1-standard-1               192.168.5.2  104.197.250.32  RUNNING
```

このInstanceにssh接続を試みても、firewall-ruleが無いため接続できません。

## firewall-ruleを追加する

新しく作ったnetworkにもsshを許可するfirewall-ruleを追加します。
default networkでは制限がゆるいfirewall-ruleだったので、指定したInstanceのみがssh接続できるように制限をきつくしましょう。

firewall-ruleを設定する上で重要な要素にtagがあります。
tagはInstanceに設定でき、firewall-ruleはIP AddrのRangeの指定と、tagの指定を選択することができます。
例えば `ssh` tagが付いているInstanceのみtcp:22を許可するfirewall-ruleを作成できます。
tagはInstanceに自由に取り付けと取り外しを行えます。
ssh接続する時にだけ `ssh` tagを付け、作業が終わったら、 `ssh` tagを外すことができます。

```
gcloud compute firewall-rules \
create sample-net-allow-ssh \
--allow tcp:22 \
--network sample-net \
--target-tags ssh \
--source-ranges 0.0.0.0/0

Created [https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/firewalls/sample-net-allow-ssh].
NAME                  NETWORK     SRC_RANGES  RULES   SRC_TAGS  TARGET_TAGS
sample-net-allow-ssh  sample-net  0.0.0.0/0   tcp:22            ssh
```

### Instanceに `ssh` tagを設定する

```
gcloud compute instances add-tags sample --zone us-central1-b --tags ssh

Updated [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample].
```

### ssh接続できることを確認する

```
gcloud compute ssh sample --zone us-central1-b
```

### Instanceから `ssh` tagを外す

```
gcloud compute instances remove-tags sample --zone us-central1-b --tags ssh

Updated [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample].
```

### ssh接続できなくなることを確認する

```
gcloud compute ssh sample --zone us-central1-b

ssh: connect to host 104.197.250.32 port 22: Operation timed out
ERROR: (gcloud.compute.ssh) [/usr/bin/ssh] exited with return code [255]. See https://cloud.google.com/compute/docs/troubleshooting#ssherrors for troubleshooting hints.
```

## Clean Up

Instaceを削除する

```
gcloud compute instances delete sample --zone us-central1-b

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/zones/us-central1-b/instances/sample].
```

firewall-ruleを削除する

```
gcloud compute firewall-rules delete sample-net-allow-ssh

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/firewalls/sample-net-allow-ssh].
```

subnetを削除する

```
gcloud compute networks subnets delete build-subnet --region us-central1

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/regions/us-central1/subnetworks/build-subnet].
```

networkを削除する

```
gcloud compute networks delete sample-net

Deleted [https://www.googleapis.com/compute/v1/projects/cpo200demo1/global/networks/sample-net].
```
