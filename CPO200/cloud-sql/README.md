# cpo200-cloud-sql

## Compute EngineからCloud SQL Proxyを利用して、Cloud SQL v2へ接続を行う

### Google Cloud SQL APIをEnableにする

Cloud SQL Proxyのために、Google Cloud SQL APIをENABLEDにします。

API Manager -> ENABLE API -> "Google Cloud SQL API"を検索 -> ENABLE

### Compute Engine Instanceを作成

Cloud SQL ProxyのためにCloud SQLのAPIを使うため --scopesに `https://www.googleapis.com/auth/sqlservice.admin` を追加して、インスタンスを作成します。

```
gcloud compute instances create "db-client" --zone "us-central1-b" --machine-type "f1-micro" \
--scopes "https://www.googleapis.com/auth/sqlservice.admin",\
"https://www.googleapis.com/auth/servicecontrol",\
"https://www.googleapis.com/auth/service.management.readonly",\
"https://www.googleapis.com/auth/logging.write",\
"https://www.googleapis.com/auth/monitoring.write",\
"https://www.googleapis.com/auth/trace.append",\
"https://www.googleapis.com/auth/devstorage.read_only"
```

### Cloud SQL v2 Instanceを作成

```
gcloud beta sql instances create db --tier=db-f1-micro --activation-policy=ALWAYS
gcloud sql instances set-root-password db --password PASSWORD
```

### Cloud SQL v2 Instanceに接続できるように、Compute Engineを設定する

```
gcloud compute ssh db-client --zone us-central1-b
```

#### mysql-client Install

```
sudo apt-get update
sudo apt-get install mysql-client
```

#### Cloud SQL v2 Proxy Install

```
wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64
mv cloud_sql_proxy.linux.amd64 cloud_sql_proxy
chmod +x cloud_sql_proxy
```

#### Cloud SQL Proxy Start

Cloud SQL Proxyを起動すると、 `127.0.0.1` への指定ポートの通信をProxyします。

```
./cloud_sql_proxy -instances={your project id}:us-central1:db=tcp:3306 &
```

Cloud SQL Proxyへ接続

```
mysql -u root -p --host 127.0.0.1
```

## Clean Up

```
gcloud compute instances delete db-client --zone us-central1-b
gcloud beta sql instances delete db
```

## Resources

* [MySQL クライアントを Compute Engine から接続する](https://cloud.google.com/sql/docs/compute-engine-access)
* [Cloud SQL Proxy Docker イメージを使用して MySQL クライアントに接続する](https://cloud.google.com/sql/docs/mysql-connect-docker)
