SELECT
  CASE
    WHEN (DAYOFWEEK(pickup_datetime) = 1) THEN 1
    ELSE 0
  END AS sunday,
  CASE
    WHEN (DAYOFWEEK(pickup_datetime) = 2) THEN 1
    ELSE 0
  END AS monday,
  CASE
    WHEN (DAYOFWEEK(pickup_datetime) = 3) THEN 1
    ELSE 0
  END AS tuesday,
  CASE
    WHEN (DAYOFWEEK(pickup_datetime) = 4) THEN 1
    ELSE 0
  END AS wednesday,
  CASE
    WHEN (DAYOFWEEK(pickup_datetime) = 5) THEN 1
    ELSE 0
  END AS thursday,
  CASE
    WHEN (DAYOFWEEK(pickup_datetime) = 6) THEN 1
    ELSE 0
  END AS friday,
  CASE
    WHEN (DAYOFWEEK(pickup_datetime) = 7) THEN 1
    ELSE 0
  END AS saturday,
  -- DAYOFWEEK(pickup_datetime) AS dayofweek,
  HOUR(pickup_datetime) AS hourofday,
  pickup_longitude,
  pickup_latitude,
  dropoff_longitude,
  dropoff_latitude,
  passenger_count AS passenger_count,
  (tolls_amount + fare_amount) AS fare_amount
FROM
  [nyc-tlc:yellow.trips]
WHERE
  trip_distance > 0
  AND fare_amount >= 2.5
  AND pickup_longitude > -78
  AND pickup_longitude < -70
  AND dropoff_longitude > -78
  AND dropoff_longitude < -70
  AND pickup_latitude > 37
  AND pickup_latitude < 45
  AND dropoff_latitude > 37
  AND dropoff_latitude < 45
  AND passenger_count > 0
  AND ABS(HASH(pickup_datetime)) % 100000 == {}
