# Lab3a: Cloud Machine Learning

以下の作業は Cloud Shell 上で行うことを想定しています。
gcloud SDK がインストールされていればローカルで作業をすることも可能です。

## Job 実行までの最短手順

### サンプルコードのダウンロード

```sh
git clone https://github.com/topgate/training-gcp.git
cd CPB102/lab3a
```

### シェル変数の定義

後々使い回すために、プロジェクト ID と作業用の bucket 名をシェル変数に入れておきましょう。

```sh
PROJECT_ID=`gcloud config list project --format "value(core.project)"`
```

### Cloud Storage のバケット作成

```sh
gsutil mb -c regional -l us-central1 gs://${PROJECT_ID}-ml
```

### データセットの準備

学習用データの csv ファイルを Google Cloud Storage に移動させておきます。

```sh
gsutil cp data/taxi-[a-zA-Z]*.csv gs://${BUCKET_NAME}/dataset/taxifare/
```

### Job の実行

Job 名はプロジェクト内で一意でなければならないので、日付や時間の情報を入れて作成するのがおすすめです。

```sh
JOB_NAME="taxifare`date '+%Y%m%d%H%M%S'`"
touch .dummy && gsutil mv .dummy gs://${PROJECT_ID}-ml/taxifare/${JOB_NAME}/model/

gcloud beta ml jobs submit training ${JOB_NAME} \
  --package-path=trainer \
  --module-name=trainer.task \
  --staging-bucket="gs://${PROJECT_ID}-ml" \
  --region=us-central1 \
  --config=config.yaml \
  -- \
  --output_path=gs://${PROJECT_ID}-ml/taxifare/${JOB_NAME}
```

### モデルのデプロイ

2017-02-04 時点ではまだ alpha ですが Cloud ML には TensorFlow で学習したモデルをデプロイできる機能があるので試してみましょう。
`trainer/task.py` では `$gs://${PROJECT_ID}-ml/taxifare/{JOB_NAME}/model/` 以下に学習済みのモデルを保存しています。

```sh
gcloud beta ml models create taxifare
gcloud beta ml models versions create v1 --model taxifare --origin gs://${PROJECT_ID}-ml/taxifare/${JOB_NAME}/model
```

### モデルを使ってみる

```sh
gcloud beta ml predict --model=taxifare --json-instances=sample.json
```