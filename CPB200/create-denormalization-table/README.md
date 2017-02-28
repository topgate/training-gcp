# cpb200-create-denormalization-table

正規化されているテーブルたちをまとめて非正規化テーブルを作ろう。

## 非正規化テーブルの作成

正規化されている受注データテーブルなどを元に、非正規化テーブルを作成する。

### 正規化されているテーブル

* 受注データ : cpb200demo1.gcpug.sale
* 受注明細データ : cpb200demo1.gcpug.detail
* 顧客マスタ : cpb200demo1.gcpug.customer
* 商品マスタ : cpb200demo1.gcpug.item

以下のQueryを `Destination Table` を指定して、中間テーブルを作成する。

```
#standardSQL

SELECT
  S.Number,
  S.Customer AS CustomerNumber,
  C.Name AS CustomerName,
  S.CreatedAt,
  ARRAY_AGG(STRUCT(D.DetailNumber,
      D.ItemNumber,
      I.Name AS ItemName,
      D.UnitPrice,
      D.OrderQuantity)) AS Details
FROM
  `cpb200demo1.gcpug.detail` D
JOIN
  `cpb200demo1.gcpug.sale` S
ON
  D.SaleNumber = S.Number
JOIN
  `cpb200demo1.gcpug.customer` C
ON
  S.Customer = C.Number
JOIN
  `cpb200demo1.gcpug.item` I
ON
  D.ItemNumber = I.Number
GROUP BY
  1,
  2,
  3,
  4
```

## 非正規化テーブルにクエリを実行

```
#standardSQL

SELECT
  CustomerNumber,
  SUM(UnitPrice * OrderQuantity) AS sale
FROM
  `cpb200demo1.gcpug.join_sale` AS t
JOIN
  UNNEST(t.Details) AS `sales`
GROUP BY
  1
```