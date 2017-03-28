# cpo200-audit-log

Compute EngineのAPIを実行した時にAudit Logを出力します。
Audit LogはCloud Loggingに出力され、確認することができます。

## Step 1

Cloud LoggingでAudit Logを確認します。

* Developer Consoleから、Cloud Loggingを選択します。
* ResourceからGCE VM Instanceを選択します。

## Step 2

Cloud LoggingでAudit Logにfilteringをかけます。

GCE InstanceのAudit Log一覧を取得します。
Filter 条件のText Boxに以下を入れます。

```
resource.type="gce_instance"
protoPayload.@type:"type.googleapis.com/google.cloud.audit.AuditLog"
```

## Step 3

Cloud Loggingは最近実行されたAudit Logを見るには便利ですが、古いデータを見たり、集計を行うことはできません。
そのようなことがしたい場合は、Cloud LoggingのデータをBigQueryにExportするようにします。

* Cloud Logging -> Exportを選択
* CREATE Exportを選択

* Sink Name = "gce_instance_auditlog"
* Sink Service = "bigquery"
* Sink Destination > `Create new BigQuery dataset` = "gce_instance_auditlog"
* Update Sinkボタンを選択

これで、Audit LogがBigQueryに自動的に入ってくるようになりました。

以下のクエリを実行してみます。
このクエリは直近7日間で、ユーザ毎にクエリを実行したバイト数と回数を集計するクエリです。

```
SELECT
  protopayload_google_cloud_audit_auditlog.authenticationInfo.principalEmail User,
  ROUND((total_bytes*5)/1000000000000, 2) Total_Cost_For_User,
  Query_Count
FROM (
  SELECT
    protopayload_google_cloud_audit_auditlog.authenticationInfo.principalEmail,
    SUM(protopayload_google_cloud_audit_auditlog.servicedata_google_cloud_bigquery_logging_v1_auditdata.jobCompletedEvent.job.jobStatistics.totalBilledBytes) AS total_bytes,
    COUNT(protopayload_google_cloud_audit_auditlog.authenticationInfo.principalEmail) AS query_count,
  FROM
    TABLE_DATE_RANGE(bigquery.cloudaudit_googleapis_com_data_access_, DATE_ADD(CURRENT_TIMESTAMP(), -7, 'DAY'), CURRENT_TIMESTAMP())
  WHERE
    protopayload_google_cloud_audit_auditlog.servicedata_google_cloud_bigquery_logging_v1_auditdata.jobCompletedEvent.eventName = 'query_job_completed'
  GROUP BY
    protopayload_google_cloud_audit_auditlog.authenticationInfo.principalEmail
    )
ORDER BY
  2 DESC
```

## Step 4

以下のクエリを実行してみましょう。
このクエリは直近7日間で、インスタンス名がinstance-1のAuditLogを取得するクエリです。

```
#standardSQL
SELECT
  protopayload_google_cloud_audit_auditlog.resourceName,
  protopayload_google_cloud_audit_auditlog.methodName,
  protopayload_google_cloud_audit_auditlog.authenticationInfo.principalEmail,
  severity,
  timestamp
FROM
  `cpo200demo1.gce_instance_auditlog.cloudaudit_googleapis_com_activity_*`
WHERE
  protopayload_google_cloud_audit_auditlog.resourceName LIKE "%instances/instance-1"
  AND _TABLE_SUFFIX BETWEEN FORMAT_DATE("%Y%m%d",
    DATE_SUB(CURRENT_DATE(),
      INTERVAL 7 DAY))
  AND FORMAT_DATE("%Y%m%d",
    CURRENT_DATE())
ORDER BY
  timestamp DESC
```

## Step 5

以下のクエリを実行してみましょう。
このクエリは直近7日間で、インスタンスのタグに `ssh-server` を設定しているAuditLogを取得するクエリです。
```
#standardSQL
SELECT
  protopayload_google_cloud_audit_auditlog.resourceName,
  protopayload_google_cloud_audit_auditlog.methodName,
  protopayload_google_cloud_audit_auditlog.authenticationInfo.principalEmail,
  protopayload_google_cloud_audit_auditlog.request_compute_googleapis_com_compute_instances_settags.tags,
  severity,
  timestamp
FROM
  `cpo200demo1.gce_instance_auditlog.cloudaudit_googleapis_com_activity_*`
WHERE
  protopayload_google_cloud_audit_auditlog.methodName = "v1.compute.instances.setTags"
  AND "ssh-server" IN UNNEST(protopayload_google_cloud_audit_auditlog.request_compute_googleapis_com_compute_instances_settags.tags)
  AND _TABLE_SUFFIX BETWEEN FORMAT_DATE("%Y%m%d",
    DATE_SUB(CURRENT_DATE(),
      INTERVAL 7 DAY))
  AND FORMAT_DATE("%Y%m%d",
    CURRENT_DATE())
ORDER BY
  timestamp DESC
```
