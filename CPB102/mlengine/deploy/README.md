# Lab: Deploy TensorFlow Model to ML Engine

Lab: Training on Cloud ML Engine の続きです。

現時点では beta 版ですが ML Engine には TensorFlow で学習したモデルをデプロイできる機能があるので試してみましょう。

`trainer/task.py` では `gs://${BUCKET_NAME}/mnist/{JOB_NAME}/model/` 以下に学習済みのモデルを保存しています。

## デプロイの手順

```sh
MODEL_NAME=mnist_${USER//_/}
gcloud ml-engine models create ${MODEL_NAME} --regions us-central1
gcloud ml-engine versions create v1 --model ${MODEL_NAME} --origin gs://${BUCKET_NAME}/mnist/${JOB_NAME}/model
```

## モデルを使ってみる

### gcloud

```sh
cd ~/training-gcp/CPB102/mlengine/deploy
gcloud ml-engine predict --model=${MODEL_NAME} --json-instances=sample.json
```

### Python

gcloud コマンドを使わずともコードの中で ML Engine にデプロイしたモデルを呼び出すこともできます。
サンプルコードを用意したので次のコマンドで試してみてください。

```sh
PROJECT_ID=`gcloud config list project --format "value(core.project)"`

python predict.py --project ${PROJECT_ID} --model ${MODEL_NAME}
```

デプロイしたモデルの呼び出しは Python に限らず [Google API Client Libraries](https://developers.google.com/api-client-library/) を使えば様々な言語で実装することが可能です。
