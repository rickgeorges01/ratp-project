#!/usr/bin/env python3
"""
A modifier
Script principal (mode batch/streaming)
"""
import json
import time
import os
from kafka import KafkaProducer


def test_kafka_connection():
    try:
        servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
        print(f"Connexion Kafka: {servers}")

        producer = KafkaProducer(
            bootstrap_servers=[servers],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )

        print("Kafka connecté!")
        return producer
    except Exception as e:
        print(f"Erreur Kafka: {e}")
        return None


def send_test_data(producer):
    """Envoi données test toutes les 30s"""
    counter = 0

    while True:
        if producer:
            test_data = {
                "station": "auber",
                "timestamp": time.time(),
                "pm10": 50 + (counter % 20),
                "pm25": 25 + (counter % 15),
                "counter": counter
            }

            try:
                producer.send('pm10-data', test_data)
                print(f"Envoyé: {test_data}")
                counter += 1
            except Exception as e:
                print(f"Erreur envoi: {e}")

        time.sleep(30)


if __name__ == "__main__":
    print("Démarrage Producer Test")
    producer = test_kafka_connection()

    if producer:
        send_test_data(producer)
    else:
        print("Producer failed - retry in 60s")
        time.sleep(60)