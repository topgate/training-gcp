# Lab3a: Cloud Machine Learning

以下の作業は Cloud Shell 上で行うことを想定しています。
gcloud SDK がインストールされていればローカルで作業をすることも可能です。

## Job 実行までの最短手順

### サンプルコードのダウンロード

```sh
git clone https://github.com/topgate/cpb102.git
cd lab3a
```

### シェル変数の定義

後々使い回すために、プロジェクト ID と作業用の bucket 名をシェル変数に入れておきましょう。

```sh
PROJECT_ID=`gcloud config list project --format "value(core.project)"`
BUCKET_NAME=${PROJECT_ID}-ml
```

### データセットの準備

公式のリポジトリから lab1a の手順で加工済みの csv ファイルをダウンロードします。

```sh
wget https://raw.githubusercontent.com/GoogleCloudPlatform/training-data-analyst/master/CPB102/lab1a/taxi-test.csv
wget https://raw.githubusercontent.com/GoogleCloudPlatform/training-data-analyst/master/CPB102/lab1a/taxi-train.csv
wget https://raw.githubusercontent.com/GoogleCloudPlatform/training-data-analyst/master/CPB102/lab1a/taxi-valid.csv
```

ダウンロードした csv ファイルを Google Cloud Storage に移動させておきます。

```sh
gsutil mv taxi-[a-zA-Z]*.csv gs://${BUCKET_NAME}/dataset/taxifare/
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
