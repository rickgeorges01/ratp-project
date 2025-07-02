from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

def main():
    spark = SparkSession.builder \
        .appName("RATP_ETL_Job") \
        .getOrCreate()

    # Config MinIO
    hadoop_conf = spark._jsc.hadoopConfiguration()
    hadoop_conf.set("fs.s3a.endpoint", "http://minio:9000")
    hadoop_conf.set("fs.s3a.access.key", "minioadmin")
    hadoop_conf.set("fs.s3a.secret.key", "minioadmi123")
    hadoop_conf.set("fs.s3a.path.style.access", "true")
    hadoop_conf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

    # --- Lecture Air Quality ---
    air_df = spark.read.option("header", True).option("sep", ";") \
        .csv("s3a://ratp-raw/batch/air_quality.csv") \
        .withColumn("DATE_HEURE", to_timestamp("DATE/HEURE")) \
        .drop("DATE/HEURE")

    # Remplacer virgule par point pour les floats
    for colname in ["TEMP", "HUMI"]:
        air_df = air_df.withColumn(colname, regexp_replace(colname, ",", "."))

    # Cast colonnes en double
    cols_to_cast = {
        "NO": "double", "NO2": "double", "PM10": "double", "PM2.5": "double",
        "CO2": "double", "TEMP": "double", "HUMI": "double"
    }
    for colname, coltype in cols_to_cast.items():
        air_df = air_df.withColumn(colname, col(colname).cast(coltype))

    # On tronque à l'heure
    air_df = air_df.withColumn("DATE_HEURE", date_trunc("hour", col("DATE_HEURE")))

    # --- Lecture Traffic ---
    traffic_df = spark.read.option("header", True).option("sep", "\t") \
        .csv("s3a://ratp-raw/batch/traffic.csv") \
        .withColumn("DATE_HEURE", to_timestamp("DATE/HEURE", "yyyy-MM-dd HH:mm:ssXXX")) \
        .drop("DATE/HEURE")

    traffic_df = traffic_df.withColumn("DATE_HEURE", date_trunc("hour", col("DATE_HEURE")))

    # --- Lecture Météo (JSON) ---
    meteo_df_raw = spark.read.json("s3a://ratp-raw/streaming/*.json")

    meteo_df = meteo_df_raw.selectExpr(
        "timestamp as DATE_HEURE",
        "temperature.actual_c as temp_c",
        "temperature.feels_like_c as temp_feels_like_c",
        "atmospheric.humidity_percent as humidity",
        "atmospheric.pressure_hpa as pressure",
        "wind.speed_kmh as wind_speed",
        "precipitation.amount_mm as precipitation",
        "precipitation.type as precipitation_type",
        "conditions.weather as weather",
        "air_quality.overall_index as air_quality_index"
    ).withColumn("DATE_HEURE", to_timestamp("DATE_HEURE")) \
     .withColumn("DATE_HEURE", date_trunc("hour", col("DATE_HEURE")))

    # --- Jointure ---
    df_joined = air_df.join(traffic_df, on="DATE_HEURE", how="inner") \
                      .join(meteo_df, on="DATE_HEURE", how="left")

    # --- Écriture finale ---
    df_joined.write.mode("overwrite").parquet("s3a://ratp-curated/air_traffic_meteo_merged/")

    spark.stop()

if __name__ == "__main__":
    main()
