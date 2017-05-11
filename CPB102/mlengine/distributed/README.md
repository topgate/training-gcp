# Distributed TensorFlow

## ジョブ実行までの手順

ML Engine に渡すコードが変わるだけで、手順自体は分散学習でもほとんど同じです。

以下の作業は Cloud Shell 上で行うことを想定しています。
gcloud SDK がインストールされていればローカル環境で作業をすることも可能です。

### サンプルコードのダウンロード

```sh
git clone https://github.com/topgate/training-gcp.git
cd training-gcp/CPB102/mlengine/distributed
```

### シェル変数の準備

後々使い回すために、プロジェクト ID と作業用のバケット名をシェル変数に入れておきましょう。

```sh
PROJECT_ID=`gcloud config list project --format "value(core.project)"`
BUCKET_NAME=${PROJECT_ID}-${USER//_/}-ml
```

### Cloud Storage のバケット作成

学習済みのモデルなどを保存するために Cloud Storage のバケットを用意しておきます。

```sh
gsutil mb -c regional -l us-central1 gs://${BUCKET_NAME}
```

### Cloud ML Engine 上での学習

Job 名はプロジェクト内で一意でなければならないので、日付や時間の情報を入れて作成するのがおすすめです。

```
JOB_NAME="mnist`date '+%Y%m%d%H%M%S'`"

gcloud ml-engine jobs submit training ${JOB_NAME} \
  --package-path=trainer \
  --module-name=trainer.task \
  --staging-bucket="gs://${BUCKET_NAME}" \
  --region=us-central1 \
  --config=config.yaml \
  -- \
  --dir=gs://${BUCKET_NAME}/mnist/${JOB_NAME}
```

## 付録

### ローカル環境で実行

```sh
gcloud ml-engine local train --module-name trainer.task \
  --package-path trainer \
  --distributed \
  --parameter-server-count 2 \
  --worker-count 2 \
  -- \
  --dir mnist
```
