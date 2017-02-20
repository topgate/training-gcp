# cpb200-json-function

JSON FunctionsはJSONで保存されている文字列から、[JSONPath](https://code.google.com/archive/p/jsonpath/) likeな構文を使って、JSONの中のデータを抜き出すことできます。

[Document](https://cloud.google.com/bigquery/query-reference#jsonfunctions)

データをJSONで登録することでスキーマ変更を柔軟に行うことができます。
データを投入するクライアントを更新することが難しい場合、JSONで登録できるのは大きな利点となります。
しかし、JSONでデータを投入し、JSON Functionでクエリを実行した場合、課金対象はJSONのデータ全体となってしまうので、コストは高くなってしまいます。
また、クエリ実行時に文字列全体を解析しなければならないので、パフォーマンスも落ちてしまいます。
しかし、ほとんどのケースでパフォーマンスはBigQueryで解決してくれるので、問題になるケースは少ないでしょう。
スキーマの柔軟性とコストとパフォーマンスのトレードオフを考えて、使うとよいです。

## Step 1 JSON_EXTRACTを試す

以下のクエリを実行してみましょう。
bの値がJSON文字列形式として取得できます。

```
SELECT
      JSON_EXTRACT('{"a": 1, "b": [4, 5]}', '$.b') AS str;
```

## Step 2 JSON_EXTRACT_SCALARを試す

以下のクエリを実行してみましょう。
$.a[1].bの値がスカラー(文字列や数字)のJSON値として取得できます。

```
SELECT
      JSON_EXTRACT_SCALAR('{"a": ["x", {"b":3}]}', '$.a[1].b') AS str;
```

## Step 3 JSONの項目を抜き出してViewを作る

ログに出力されたJSONのデータを読み込み、Viewを作成する

まず、ログに出力されたJSONのデータを確認する。

```
SELECT
  textPayload
FROM
  [cp300demo1:computeengine.syslog_20150803]
WHERE
  textPayload CONTAINS "__SAMPLE__"
ORDER BY
  metadata.timestamp DESC
LIMIT
  100
```

### Sample Data

```
Aug 3 11:54:51 preem-y7z5 startupscript: {"__SAMPLE__":{ "kind": "storage#object", "id": "cp300demo1-ocn/Datastore_Admin_-_iketeru-ui-dev.png/1438602829398000", "selfLink": "https://www.googleapis.com/storage/v1/b/cp300demo1-ocn/o/Datastore_Admin_-_iketeru-ui-dev.png", "name": "Datastore_Admin_-_iketeru-ui-dev.png", "bucket": "cp300demo1-ocn", "generation": "1438602829398000", "metageneration": "1", "contentType": "image/png", "updated": "2015-08-03T11:53:49.397Z", "storageClass": "STANDARD", "size": "363457", "md5Hash": "HPYnvfM+ThYQYxM1LyAkdA==", "mediaLink": "https://www.googleapis.com/download/storage/v1/b/cp300demo1-ocn/o/Datastore_Admin_-_iketeru-ui-dev.png?generation=1438602829398000&alt=media", "owner": { "entity": "user-00b4903a97ed1f23bc6c49b74d47aaf29cabf5b359e1dbb1d98519b04b3667c2", "entityId": "00b4903a97ed1f23bc6c49b74d47aaf29cabf5b359e1dbb1d98519b04b3667c2" }, "crc32c": "+BaM9w==", "etag": "CPD/+ZTtjMcCEAE="}}
```

JSONの部分だけを抜き出したいので、REGEXP_REPLACEを利用して、JSONより前の余計な部分を除いて取得する

```
SELECT
  REGEXP_REPLACE(textPayload, r'.*{"__SAMPLE__', '{"__SAMPLE__') AS json
FROM
  [cp300demo1:computeengine.syslog_20150803]
WHERE
  textPayload CONTAINS "__SAMPLE__"
```

JSONから試しにidのnodeを抜き出してみる

```
SELECT
  JSON_EXTRACT_SCALAR(json, '$.__SAMPLE__.id') AS id
FROM (
  SELECT
    REGEXP_REPLACE(textPayload, r'.*{"__SAMPLE__', '{"__SAMPLE__') AS json
  FROM
    [cp300demo1:computeengine.syslog_20150803]
  WHERE
    textPayload CONTAINS "__SAMPLE__" )
```

残りの全nodeを抜き出してみる。
クエリを実行した後、SaveViewボタンを押し、View名を付けて保存しておく。

```
SELECT
  JSON_EXTRACT_SCALAR(json, '$.__SAMPLE__.id') AS id,
  JSON_EXTRACT_SCALAR(json, '$.__SAMPLE__.kind') AS kind,
  JSON_EXTRACT_SCALAR(json, '$.__SAMPLE__.selfLink') AS selfLink,
  JSON_EXTRACT_SCALAR(json, '$.__SAMPLE__.name') AS name,
  JSON_EXTRACT_SCALAR(json, '$.__SAMPLE__.bucket') AS bucket,
  JSON_EXTRACT_SCALAR(json, '$.__SAMPLE__.generation') AS generation,
  JSON_EXTRACT_SCALAR(json, '$.__SAMPLE__.metageneration') AS metageneration,
  JSON_EXTRACT_SCALAR(json, '$.__SAMPLE__.contentType') AS contentType,
  JSON_EXTRACT_SCALAR(json, '$.__SAMPLE__.updated') AS updated,
  JSON_EXTRACT_SCALAR(json, '$.__SAMPLE__.storageClass') AS storageClass,
  JSON_EXTRACT_SCALAR(json, '$.__SAMPLE__.size') AS size,
  JSON_EXTRACT_SCALAR(json, '$.__SAMPLE__.md5Hash') AS md5Hash,
  JSON_EXTRACT_SCALAR(json, '$.__SAMPLE__.mediaLink') AS mediaLink,
  JSON_EXTRACT_SCALAR(json, '$.__SAMPLE__.crc32c') AS crc32c,
  JSON_EXTRACT_SCALAR(json, '$.__SAMPLE__.etag') AS etag
FROM (
  SELECT
    REGEXP_REPLACE(textPayload, r'.*{"__SAMPLE__', '{"__SAMPLE__') AS json
  FROM
    [cp300demo1:computeengine.syslog_20150803]
  WHERE
    textPayload CONTAINS "__SAMPLE__" )
```

Viewに対してクエリを実行する

```
SELECT
  bucket,
  COUNT(bucket) AS count
FROM
  [{your table}]
GROUP BY
  bucket
LIMIT
  1000
```
