# cpo200-cloud-storage

## Bucketの作成

Coldline BucketをUSに作成

```
gsutil mb -c coldline -l US gs://{your bucket}-cold
```

Nearline BucketをUSに作成

```
gsutil mb -c nearline -l US gs://{your bucket}-near
```

Regional Bucketをasia-northeast1に作成

```
gsutil mb -c regional -l asia-northeast1 gs://{your bucket}-regional
```

Multi Regional BucketをASIAに作成

```
gsutil mb -l asia gs://{your bucket}-multi-regional
```

bucket 一覧を確認する

```
gsutil ls

gs://cpo200demo1-cold/
gs://cpo200demo1-dra/
gs://cpo200demo1-multi-regional/
gs://cpo200demo1-near/
gs://cpo200demo1-regional/
gs://cpo200demo1.appspot.com/
```

## BucketにファイルをUploadする

適当なファイルを作成

```
echo 1 > 1.txt
echo 2 > 2.txt
```

ファイルをUploadする
-m optionはパラレル実行のためのオプションで、たくさんのファイルをやり取りする時に設定すると、早く終わるようになる。

```
gsutil -m cp "*.txt" gs://{your bucket}

Copying file://2.txt [Content-Type=text/plain]...
Copying file://1.txt [Content-Type=text/plain]...
Uploading   gs://{your bucket}/1.txt:                              2 B/2 B
Uploading   gs://{your bucket}/2.txt:                              2 B/2 B
```

## Cloud Storageのファイルを結合する

compose機能を使うと、Cloud Storageにある複数のファイルを結合できます。
1.txt, 2.txtを結合して、composite.txtを作成してみます。

```
gsutil compose "gs://{your bucket}demo1/*.txt" gs://{your bucket}demo1/composite.txt

Composing gs://{your bucket}demo1/composite.txt from 2 component objects.
```

できあがったファイルを確認する

```
gsutil ls gs://{your bucket}demo1

gs://{your bucket}demo1/1.txt
gs://{your bucket}demo1/2.txt
gs://{your bucket}demo1/composite.txt
```

1.txt, 2.txtを結合したので、12と書いてあるファイルができあがりました

```
gsutil cat gs://{your bucket}demo1/composite.txt
1
2
```

composeできる数は1024という制限があります。
composeされている数はmeta情報のComponent-Countの値を見ることが分かります。

```
gsutil ls -L gs://{your bucket}demo1/composite.txt

gs://{your bucket}demo1/composite.txt:
	Creation time:		Mon, 26 Sep 2016 11:37:41 GMT
	Content-Length:		4
	Content-Type:		text/plain
	Component-Count:	2
	Hash (crc32c):		0LQiVA==
	ETag:			CMC6sPL4rM8CEAE=
	Generation:		1474889861832000
	Metageneration:		1
	ACL:		[
...
]
TOTAL: 1 objects, 4 bytes (4 B)
```

### Clean Up

```
gsutil -m rm "gs://{your bucket}demo1/*"

Removing gs://{your bucket}demo1/1.txt...
Removing gs://{your bucket}demo1/2.txt...
Removing gs://{your bucket}demo1/composite.txt...
```

## Versioning

Cloud StorageはObjectのVersioningが行えます。
誤ってファイルを上書きしたり、消してしまった場合に、元のファイルが消えないようになります。
ただし、そのぶん、ストレージ容量は使うので、料金は高くなります。

VersioningはBucket単位で設定します。
`gsutil versioning set on` で設定、 `gsutil versioning set off` で止めることができます。

```
gsutil versioning set on gs://{your bucket}

Enabling versioning for gs://{your bucket}/...
```

versionをonにした状態で、ファイルを同じPathにUploadしてみます。

```
echo 1 | gsutil cp - gs://{your bucket}/1.txt

Copying from <STDIN>...
/ [1 files][    0.0 B/    0.0 B]
Operation completed over 1 objects.
```

1.txt を `2` で上書き

```
echo 2 | gsutil cp - gs://{your bucket}/1.txt
Copying from <STDIN>...
/ [1 files][    0.0 B/    0.0 B]
Operation completed over 1 objects.
```

1.txtの中身は `2` となった。

```
gsutil cat gs://{your bucket}/1.txt
2
```

`-a` optionを付けると、過去のversionも表示される。

```
gsutil ls -a gs://{your bucket}

gs://{your bucket}/1.txt#1474890799504000
gs://{your bucket}/1.txt#1474890815454000
```

古いversionのObjectをcatすると、その時点の内容が返ってくる

```
gsutil cat gs://{your bucket}/1.txt#1474890799504000
1
```

1.txtを削除

```
gsutil rm gs://{your bucket}/1.txt

Removing gs://{your bucket}/1.txt...
/ [1 objects]
Operation completed over 1 objects.
```

lsを中身を見ると空っぽ

```
gsutil ls gs://{your bucket}
```

`ls -a` だと、削除されたObjectも表示される。

```
gsutil ls -a gs://{your bucket}

gs://{your bucket}demo1/1.txt#1474890799504000
gs://{your bucket}demo1/1.txt#1474890815454000
```

`rm -a` で削除すると、過去Versionも含めて全て削除される。

```
gsutil rm -a gs://{your bucket}/1.txt

Removing gs://{your bucket}demo1/1.txt#1474890799504000...
Removing gs://{your bucket}demo1/1.txt#1474890815454000...
/ [2 objects]
Operation completed over 2 objects.
```

## Lifecycle

### 指定した条件を満たしたものを削除

Lifecycleで指定した条件を満たしたObjectを自動的に削除する。
work bucketのObjectの削除や、Versioningを設定しているbucketで古いversionのObjectを削除するなどに利用する。

Lifecycleの条件はjsonで行うので、設定用のjsonを用意する。

作成されてから1日後に存在しているObjectを削除、Objectの最新バージョンを3つ保持する設定のjson

```
gsutil cp gs://cpo200demo1-lifecycle-json/lifecycle-age1-numNewerVersions3.json .

cat lifecycle-age1-numNewerVersions3.json
{
  "rule": [
   {
    "action": {
     "type": "Delete"
    },
    "condition": {
     "age": 1,
     "isLive": true
    }
   },
   {
    "action": {
     "type": "Delete"
    },
    "condition": {
     "isLive": false,
     "numNewerVersions": 3
    }
   }
  ]
}
```

lifecycleの設定

```
gsutil lifecycle set lifecycle-age1-numNewerVersions3.json gs://{your bucket}

Setting lifecycle configuration on gs://{your bucket}/...
```

設定されているlifecycleの確認

```
gsutil lifecycle get gs://{your bucket}
{"rule": [{"action": {"type": "Delete"}, "condition": {"age": 1, "isLive": true}}, {"action": {"type": "Delete"}, "condition": {"isLive": false, "numNewerVersions": 3}}]}
```

### 指定した条件を満たしたものを違うStorageClassに移動

Lifecycleで指定した条件を満たしたObjectを指定したStorageClassに移動する。
過去データでほとんどアクセスされることがないものを、Storage料金の安いclassに移動させる。

Lifecycleの条件はjsonで行うので、設定用のjsonを用意する。

作成されてから365日経過しておりMultiRegional, Standard, DRAにあるものは、Nearlineへ移動
作成されてから1095日経過してNearlineにあるものは、Coldlineへ移動

```
gsutil cp gs://cpo200demo1-lifecycle-json/lifecycle-storageclass.json .

cat lifecycle-storageclass.json
{
	"lifecycle": {
		"rule": [{
			"action": {
				"type": "SetStorageClass",
				"storageClass": "NEARLINE"
			},
			"condition": {
				"age": 365,
				"matchesStorageClass": ["MULTI_REGIONAL", "STANDARD", "DURABLE_REDUCED_AVAILABILITY"]
			}
		}, {
			"action": {
				"type": "SetStorageClass",
				"storageClass": "COLDLINE"
			},
			"condition": {
				"age": 1095,
				"matchesStorageClass": ["NEARLINE"]
			}
		}]
	}
}
```

lifecycleの設定

```
gsutil lifecycle set lifecycle-storageclass.json gs://{your bucket}

Setting lifecycle configuration on gs://{your bucket}/...
```

設定されているlifecycleの確認

```
gsutil lifecycle get gs://{your bucket}
{"rule": [{"action": {"storageClass": "NEARLINE", "type": "SetStorageClass"}, "condition": {"age": 365, "matchesStorageClass": ["MULTI_REGIONAL", "STANDARD", "DURABLE_REDUCED_AVAILABILITY"]}}, {"action": {"storageClass": "COLDLINE", "type": "SetStorageClass"}, "condition": {"age": 1095, "matchesStorageClass": ["NEARLINE"]}}]}
```

## Clean Up

Bucket内のObjectを全て削除

```
gsutil -m rm "gs://{your bucket}/*"
```

作成したBucketを削除する

```
gsutil rb gs://{your bucket}
```
