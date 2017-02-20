# cpo200-projects

## Production環境のためにGCP Projectを作成する

GCPで開発を行う場合、複数のGCP Projectを作成することがほとんどです。
少なくとも、開発用,本番用の2つは必ず作成します。

このLabでは、新しいGCP Projectを作成してみましょう。

* https://console.cloud.google.com からcreate projectを選択します。
* Project Nameに `CPO200-Production` を入力し `Create` ボタンを押します。

## Project Components

### ProjectName

人間が識別するためのProjectの名前。GCP上で一意になっている必要はない。

### ProjectID

GCP上でProjectを一意に定めるためのID。よく利用するので、比較的入力しやすいものが良い。

### ProjectNumber

GCP上でProjectを一意に定めるための番号。自動採番され、あまり利用することはない。
