"""
Air quality + trafic -->  MinIO direct
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, year, month, dayofmonth, lit
import datetime
import os 

print(" Kafka servers depuis os.environ:", os.environ.get("KAFKA_BOOTSTRAP_SERVERS"))

# 📅 Date de traitement (modifiable à la main si besoin)
PROCESS_DATE = "20250702-1200"


def create_spark_session():
    return SparkSession.builder \
        .appName("BatchProducer") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
        .getOrCreate()

def save_as_partitioned_parquet(df, output_path, partition_date):
    """Ajoute les colonnes de partition et sauvegarde dans MinIO"""
    y, m, d = partition_date.split("-")
    df = df.withColumn("year", lit(int(y))) \
           .withColumn("month", lit(int(m))) \
           .withColumn("day", lit(int(d))) \
           .withColumn("processed_at", current_timestamp())

    df.write.mode("overwrite") \
      .partitionBy("year", "month", "day") \
      .parquet(output_path)

def process_air_quality(spark):
    input_path = "data/air_quality_auber.csv"
    output_path = "s3a://ratp-raw/batch/pm10/"

    df = spark.read.option("header", True).csv(input_path)
    save_as_partitioned_parquet(df, output_path, PROCESS_DATE)
    print(f"PM10 sauvegardé dans {output_path}")

def process_trafic(spark):
    input_path = "data/trafic_2021.csv"
    output_path = "s3a://ratp-raw/batch/trafic/"

    df = spark.read.option("header", True).csv(input_path)
    save_as_partitioned_parquet(df, output_path, PROCESS_DATE)
    print(f"Trafic sauvegardé dans {output_path}")

if __name__ == "__main__":
    spark = create_spark_session()
    process_air_quality(spark)
    process_trafic(spark)
    spark.stop()
