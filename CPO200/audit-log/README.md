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

## Step 4

以下のクエリを実行してみましょう。
このクエリは直近7日間で、インスタンス名がinstance-1のAuditLogを取得するクエリです。

```
#standardSQL
SELECT
  protopayload_auditlog.resourceName,
  protopayload_auditlog.methodName,
  protopayload_auditlog.authenticationInfo.principalEmail,
  severity,
  timestamp
FROM
  `gce_instance_auditlog.cloudaudit_googleapis_com_activity_*`
WHERE
  protopayload_auditlog.resourceName LIKE "%instances/instance-1"
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
  protopayload_auditlog.resourceName,
  protopayload_auditlog.methodName,
  protopayload_auditlog.authenticationInfo.principalEmail,
  protopayload_auditlog.request_instances_settags.tags,
  severity,
  timestamp
FROM
  `gce_instance_auditlog.cloudaudit_googleapis_com_activity_*`
WHERE
  protopayload_auditlog.methodName = "v1.compute.instances.setTags"
  AND "ssh-server" IN UNNEST(protopayload_auditlog.request_instances_settags.tags)
  AND _TABLE_SUFFIX BETWEEN FORMAT_DATE("%Y%m%d",
    DATE_SUB(CURRENT_DATE(),
      INTERVAL 7 DAY))
  AND FORMAT_DATE("%Y%m%d",
    CURRENT_DATE())
ORDER BY
  timestamp DESC
```
