"""
Météo --> Kafka
"""
from kafka import KafkaProducer
import json
import time
import threading
from producer.weather_simulator import generate_paris_weather_data
import os

KAFKA_TOPIC = "weather"
KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
SEND_INTERVAL = int(os.getenv("SEND_INTERVAL", "30"))


producer = KafkaProducer(
    bootstrap_servers=[KAFKA_SERVER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8')
)

def send_weather_messages(thread_id, num_messages, sleep_time=2):
    for i, reading in enumerate(generate_paris_weather_data(num_messages)):
        station_key = reading["station"]["name"]
        reading["thread_id"] = thread_id
        reading["message_number"] = i

        producer.send(
            TOPIC,
            key=station_key,
            value=reading
        )
        print(f"[Thread {thread_id}] {station_key} → Kafka")
        time.sleep(sleep_time)

if __name__ == "__main__":
    threads = []
    for i in range(2):  # 2 simulateurs parallèles
        thread = threading.Thread(target=send_weather_messages, args=(i, 50))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    producer.flush()
    producer.close()
