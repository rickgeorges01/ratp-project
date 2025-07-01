#!/usr/bin/env python3
"""
A modifier
Kafka météo -->  MinIO streaming
"""
import os
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import *


def create_spark_session():
    try:
        spark = SparkSession.builder \
            .appName("RATP-Test") \
            .config("spark.sql.adaptive.enabled", "true") \
            .getOrCreate()

        print("Spark Session créée!")
        return spark
    except Exception as e:
        print(f"Erreur Spark: {e}")
        return None


def test_kafka_read(spark):
    try:
        kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')

        df = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", kafka_servers) \
            .option("subscribe", "pm10-data") \
            .option("startingOffsets", "latest") \
            .load()

        # Simple parsing
        parsed_df = df.select(
            col("timestamp").alias("kafka_timestamp"),
            col("value").cast("string").alias("json_data")
        )

        # Output console
        query = parsed_df.writeStream \
            .outputMode("append") \
            .format("console") \
            .option("truncate", False) \
            .trigger(processingTime="10 seconds") \
            .start()

        print("Spark Streaming démarré - écoute Kafka...")
        return query

    except Exception as e:
        print(f"Erreur Kafka read: {e}")
        return None


if __name__ == "__main__":
    print("Démarrage Spark Test")

    spark = create_spark_session()
    if spark:
        query = test_kafka_read(spark)

        if query:
            try:
                query.awaitTermination()
            except KeyboardInterrupt:
                print("Arrêt demandé")
                query.stop()
                spark.stop()
        else:
            print("Streaming failed")
            time.sleep(60)
    else:
        print("Spark failed")
        time.sleep(60)