#!/usr/bin/env python3
"""
A modifier
Kafka météo -->  MinIO streaming
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, year, month, dayofmonth, hour
from pyspark.sql.types import *

KAFKA_TOPIC = "weather"
KAFKA_SERVER = "kafka:9092"  # ou localhost:9092 si tu testes sans docker
S3_PATH = "s3a://ratp-raw/streaming/meteo/"

def create_spark_session():
    return SparkSession.builder \
        .appName("KafkaToMinIO") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .getOrCreate()

def main():
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    schema = StructType([
        StructField("reading_id", StringType()),
        StructField("timestamp", StringType()),
        StructField("station", StructType([
            StructField("name", StringType()),
            StructField("coordinates", StructType([
                StructField("latitude", DoubleType()),
                StructField("longitude", DoubleType())
            ])),
            StructField("department", StringType()),
            StructField("zone", StringType()),
            StructField("altitude", IntegerType())
        ])),
        StructField("temperature", StructType([
            StructField("actual_c", DoubleType()),
            StructField("feels_like_c", DoubleType())
        ])),
        StructField("atmospheric", StructType([
            StructField("humidity_percent", IntegerType()),
            StructField("pressure_hpa", DoubleType()),
            StructField("visibility_km", DoubleType())
        ])),
        StructField("wind", StructType([
            StructField("speed_kmh", DoubleType()),
            StructField("direction", StringType())
        ])),
        StructField("conditions", StructType([
            StructField("weather", StringType()),
            StructField("description", StringType())
        ]))
    ])

    df_raw = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_SERVER) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "latest") \
        .load()

    df_json = df_raw.selectExpr("CAST(value AS STRING) as json_str") \
        .select(from_json(col("json_str"), schema).alias("data")) \
        .select("data.*") \
        .withColumn("year", year("timestamp")) \
        .withColumn("month", month("timestamp")) \
        .withColumn("day", dayofmonth("timestamp")) \
        .withColumn("hour", hour("timestamp"))

    query = df_json.writeStream \
        .format("parquet") \
        .option("checkpointLocation", "/tmp/checkpoints/weather") \
        .option("path", S3_PATH) \
        .partitionBy("year", "month", "day", "hour") \
        .outputMode("append") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()
