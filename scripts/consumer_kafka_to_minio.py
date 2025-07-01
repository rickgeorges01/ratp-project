from kafka import KafkaConsumer
from minio import Minio
from minio.error import S3Error
import json
import io
from datetime import datetime
import uuid

# Configuration MinIO
endpoint = "localhost:9000"
access_key = "minioadmin"
secret_key = "minioadmin123"

client = Minio(
    endpoint,
    access_key=access_key,
    secret_key=secret_key,
    secure=False
)

BUCKET_RAW = "ratp-raw"

def ensure_bucket_exists():
    """S'assure que le bucket existe"""
    try:
        if not client.bucket_exists(BUCKET_RAW):
            client.make_bucket(BUCKET_RAW)
            print(f"✅ Bucket '{BUCKET_RAW}' créé")
    except S3Error as e:
        print(f"❌ Erreur bucket: {e}")

def send_to_minio(message_data, topic_name):
    """Envoie les données vers MinIO selon le type de message"""
    try:
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H-%M-%S")
        
        # Génération d'un ID unique
        message_id = str(uuid.uuid4())[:8]
        
        # Organisation par topic et date
        object_name = f"kafka/{topic_name}/{date_str}/{time_str}_{message_id}.json"
        
        # Si c'est de la météo, organisation spéciale
        if topic_name == "weather" and isinstance(message_data, dict):
            if "station" in message_data:
                station_info = message_data.get('station', {})
                zone = station_info.get('zone', 'unknown_zone').replace(' ', '_')
                dept = station_info.get('department', 'unknown_dept')
                hour = timestamp.strftime("%H")
                
                object_name = f"weather/{zone}/dept_{dept}/{date_str}/hour_{hour}/{message_id}.json"
        
        # Conversion en JSON
        json_data = json.dumps(message_data, indent=2, ensure_ascii=False)
        json_bytes = json_data.encode('utf-8')
        data_stream = io.BytesIO(json_bytes)
        
        # Upload vers MinIO
        client.put_object(
            BUCKET_RAW,
            object_name,
            data_stream,
            length=len(json_bytes),
            content_type="application/json"
        )
        
        print(f"📤 Message envoyé vers MinIO: {object_name}")
        return object_name
        
    except Exception as e:
        print(f"❌ Erreur envoi MinIO: {e}")
        return None

def kafka_to_minio_consumer(topics=["weather", "traffic", "air_quality"], kafka_server="localhost:9092"):
    """Consumer Kafka qui envoie directement vers MinIO"""
    
    # Initialisation
    ensure_bucket_exists()
    
    # Configuration du consumer
    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers=[kafka_server],
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='minio-consumer-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None
    )
    
    print(f"🚀 Consumer Kafka → MinIO démarré")
    print(f"📡 Topics: {topics}")
    print(f"📦 Bucket: {BUCKET_RAW}")
    print("=" * 50)
    
    try:
        for message in consumer:
            topic = message.topic
            data = message.value
            
            if data:
                print(f"📨 Message reçu depuis '{topic}'")
                
                # Envoi vers MinIO
                minio_path = send_to_minio(data, topic)
                
                if minio_path:
                    print(f"✅ Stocké: {minio_path}")
                else:
                    print(f"❌ Échec stockage topic '{topic}'")
                    
                print("-" * 30)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Arrêt du consumer")
    except Exception as e:
        print(f"❌ Erreur consumer: {e}")
    finally:
        consumer.close()
        print("🔒 Consumer fermé")

# Version simplifiée pour un seul topic
def simple_weather_consumer(kafka_server="localhost:9092"):
    """Consumer simple pour topic weather seulement"""
    
    ensure_bucket_exists()
    
    consumer = KafkaConsumer(
        'weather',
        bootstrap_servers=[kafka_server],
        auto_offset_reset='latest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    print(f"🌤️ Consumer Weather → MinIO actif")
    
    for message in consumer:
        weather_data = message.value
        
        if weather_data:
            station_name = weather_data.get('station', {}).get('name', 'Station inconnue')
            temp = weather_data.get('temperature', {}).get('actual_c', 'N/A')
            
            print(f"🌤️ Météo reçue: {station_name} | {temp}°C")
            
            minio_path = send_to_minio(weather_data, "weather")
            if minio_path:
                print(f"✅ Stocké dans MinIO")

if __name__ == "__main__":
    # Choix du mode
    mode = input("Mode consumer (1=Multi-topics, 2=Weather only): ")
    
    if mode == "2":
        simple_weather_consumer()
    else:
        # Consumer multi-topics
        kafka_to_minio_consumer(["weather", "traffic", "air_quality"])
