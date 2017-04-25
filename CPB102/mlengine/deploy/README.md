# Lab: Deploy TensorFlow Model to ML Engine



現時点では beta 版ですが ML Engine には TensorFlow で学習したモデルをデプロイできる機能があるので試してみましょう。
`trainer/task.py` では `gs://${PROJECT_ID}-ml/mnist/{JOB_NAME}/model/` 以下に学習済みのモデルを保存しています。

```sh
gcloud ml-engine models create mnist
gcloud ml-engine versions create v1 --model mnist --origin gs://${PROJECT_ID}-ml/mnist/${JOB_NAME}/model --async
```

### モデルを使ってみる

```sh
gcloud ml-engine predict --model=taxifare --json-instances=sample.json
```
