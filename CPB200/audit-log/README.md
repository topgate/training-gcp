# cpb200-audit-log

BigQueryはデータのロードや、クエリの実行など、BigQueryのAPIを実行した時にAudit Logを出力します。
Audit LogはCloud Loggingに出力され、確認することができます。

## Step 1

Cloud LoggingでAudit Logを確認します。

* Developer Consoleから、Cloud Loggingを選択します。
* ResourceからBigQueryを選択します。

## Step 2

Cloud LoggingでAudit Logにfilteringをかけます。

クエリで読み込んだデータ容量が5000000000を超えるjobの一覧を取得します。
Filter 条件のText Boxに以下を入れます。

```
resource.type="bigquery_resource"
protoPayload.serviceData.jobCompletedEvent.job.jobStatistics.totalBilledBytes > 5000000000
```

次はBillingTierの値が1より大きいクエリを探します。

```
resource.type="bigquery_resource"
protoPayload.serviceData.jobCompletedEvent.job.jobStatistics.billingTier > 1
```

## Step 3

Cloud Loggingは最近実行されたAudit Logを見るには便利ですが、古いデータを見たり、集計を行うことはできません。
そのようなことがしたい場合は、Cloud LoggingのデータをBigQueryにExportするようにします。

* Cloud Logging -> Exportを選択
* CREATE Exportを選択
* fileterをbasic modeに設定

![log_export_clear_filters_and_return_to_basic_mode](https://storage.googleapis.com/cpb200demo1.appspot.com/images/log_export_clear_filters_and_return_to_basic_mode.png "log_export_clear_filters_and_return_to_basic_mode")

* Sink Name = "bigquery"
* Sink Service = "bigquery"
* Sink Destination > `Create new BigQuery dataset` = "bigquery"
* Update Sinkボタンを選択

これで、Audit LogがBigQueryに自動的に入ってくるようになりました。

以下のクエリを実行してみます。
このクエリは直近7日間で、ユーザ毎にクエリを実行した回数と料金を集計するクエリです。

```
#standardSQL
SELECT
  protopayload_auditlog.authenticationInfo.principalEmail AS User,
  SUM(ROUND((( protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent.job.jobStatistics.totalBilledBytes *(5* protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent.job.jobStatistics.billingTier))/1000000000000),2)) Cost_In_Dollars,
  COUNT(1) As Count 
FROM
  `bigquery.cloudaudit_googleapis_com_data_access_*`
WHERE
  protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent.eventName = 'query_job_completed'
  AND _TABLE_SUFFIX BETWEEN FORMAT_DATE("%Y%m%d",
    DATE_SUB(CURRENT_DATE(),
      INTERVAL 7 DAY))
  AND FORMAT_DATE("%Y%m%d",
    CURRENT_DATE())
GROUP BY
  1
ORDER BY
  Cost_In_Dollars DESC
```

## Step 4

以下のクエリを実行してみましょう。
このクエリは直近7日間で、クエリ実行時のバイト数, BillingTierを考慮し、クエリ料金の高い順に結果を返すクエリです。

```
#standardSQL
SELECT
  protopayload_auditlog.authenticationInfo.principalEmail AS User,
  protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent.job.jobStatistics.billingTier AS billingTier,
  protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent.job.jobStatistics.totalBilledBytes AS totalBilledBytes,
  ROUND((( protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent.job.jobStatistics.totalBilledBytes *(5* protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent.job.jobStatistics.billingTier))/1000000000000),2) Cost_In_Dollars,
  protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent.job.jobConfiguration.query.query
FROM
  `bigquery.cloudaudit_googleapis_com_data_access_*`
WHERE
  protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent.eventName = 'query_job_completed'
  AND _TABLE_SUFFIX BETWEEN FORMAT_DATE("%Y%m%d",
    DATE_SUB(CURRENT_DATE(),
      INTERVAL 7 DAY))
  AND FORMAT_DATE("%Y%m%d",
    CURRENT_DATE())
ORDER BY
  Cost_In_Dollars DESC
```

## Step 5

以下のクエリを実行してみましょう。
このクエリは直近7日間で、安易にSELECT * を実行しているクエリを探し出します。
```
#standardSQL
SELECT
  protopayload_auditlog.authenticationInfo.principalEmail AS User,
  protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent.job.jobStatistics.billingTier AS billingTier,
  protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent.job.jobStatistics.totalBilledBytes AS totalBilledBytes,
  ROUND((( protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent.job.jobStatistics.totalBilledBytes *(5* protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent.job.jobStatistics.billingTier))/1000000000000),2) Cost_In_Dollars,
  protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent.job.jobConfiguration.query.query
FROM
  `bigquery.cloudaudit_googleapis_com_data_access_*`
WHERE
  protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent.eventName = 'query_job_completed'
  AND _TABLE_SUFFIX BETWEEN FORMAT_DATE("%Y%m%d",
    DATE_SUB(CURRENT_DATE(),
      INTERVAL 7 DAY))
  AND FORMAT_DATE("%Y%m%d",
    CURRENT_DATE())
  AND REGEXP_CONTAINS(LOWER(protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent.job.jobConfiguration.query.query),
    r'^select \*')
ORDER BY
  3 DESC
```
