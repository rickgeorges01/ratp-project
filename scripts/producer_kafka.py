from kafka import KafkaProducer
import time
import threading
import json
import random
import datetime
import uuid
import math

# Nom du topic Kafka
topic_name = 'weather'

# Fonction pour sérialiser les messages en JSON
def json_serializer(data):
    return json.dumps(data).encode('utf-8')

def generate_paris_weather_data(num_readings):
    """Generates realistic weather data for Paris and Île-de-France."""
    
    weather_readings = []
    
    # Stations météo Paris par arrondissement + Île-de-France
    weather_stations = {
        # Paris intra-muros (20 arrondissements)
        "Paris-1er-Louvre": {"lat": 48.8606, "lon": 2.3376, "department": "75", "zone": "Paris", "altitude": 35},
        "Paris-2e-Bourse": {"lat": 48.8698, "lon": 2.3412, "department": "75", "zone": "Paris", "altitude": 36},
        "Paris-3e-Temple": {"lat": 48.8630, "lon": 2.3626, "department": "75", "zone": "Paris", "altitude": 38},
        "Paris-4e-Hotel-de-Ville": {"lat": 48.8566, "lon": 2.3522, "department": "75", "zone": "Paris", "altitude": 34},
        "Paris-5e-Pantheon": {"lat": 48.8462, "lon": 2.3372, "department": "75", "zone": "Paris", "altitude": 61},
        "Paris-6e-Luxembourg": {"lat": 48.8462, "lon": 2.3372, "department": "75", "zone": "Paris", "altitude": 54},
        "Paris-7e-Palais-Bourbon": {"lat": 48.8566, "lon": 2.3065, "department": "75", "zone": "Paris", "altitude": 39},
        "Paris-8e-Elysee": {"lat": 48.8742, "lon": 2.3170, "department": "75", "zone": "Paris", "altitude": 43},
        "Paris-9e-Opera": {"lat": 48.8742, "lon": 2.3387, "department": "75", "zone": "Paris", "altitude": 67},
        "Paris-10e-Enclos-St-Laurent": {"lat": 48.8760, "lon": 2.3590, "department": "75", "zone": "Paris", "altitude": 40},
        "Paris-11e-Popincourt": {"lat": 48.8631, "lon": 2.3708, "department": "75", "zone": "Paris", "altitude": 50},
        "Paris-12e-Reuilly": {"lat": 48.8448, "lon": 2.3895, "department": "75", "zone": "Paris", "altitude": 45},
        "Paris-13e-Gobelins": {"lat": 48.8322, "lon": 2.3561, "department": "75", "zone": "Paris", "altitude": 42},
        "Paris-14e-Observatoire": {"lat": 48.8339, "lon": 2.3265, "department": "75", "zone": "Paris", "altitude": 59},
        "Paris-15e-Vaugirard": {"lat": 48.8422, "lon": 2.2966, "department": "75", "zone": "Paris", "altitude": 45},
        "Paris-16e-Passy": {"lat": 48.8590, "lon": 2.2742, "department": "75", "zone": "Paris", "altitude": 71},
        "Paris-17e-Batignolles": {"lat": 48.8839, "lon": 2.3154, "department": "75", "zone": "Paris", "altitude": 47},
        "Paris-18e-Montmartre": {"lat": 48.8922, "lon": 2.3444, "department": "75", "zone": "Paris", "altitude": 108},
        "Paris-19e-Buttes-Chaumont": {"lat": 48.8799, "lon": 2.3783, "department": "75", "zone": "Paris", "altitude": 63},
        "Paris-20e-Menilmontant": {"lat": 48.8649, "lon": 2.3969, "department": "75", "zone": "Paris", "altitude": 96},
        
        # Petite Couronne (92, 93, 94)
        "Boulogne-Billancourt": {"lat": 48.8414, "lon": 2.2400, "department": "92", "zone": "Hauts-de-Seine", "altitude": 37},
        "Nanterre": {"lat": 48.8924, "lon": 2.2069, "department": "92", "zone": "Hauts-de-Seine", "altitude": 40},
        "Levallois-Perret": {"lat": 48.8979, "lon": 2.2877, "department": "92", "zone": "Hauts-de-Seine", "altitude": 30},
        "Saint-Denis": {"lat": 48.9362, "lon": 2.3574, "department": "93", "zone": "Seine-Saint-Denis", "altitude": 33},
        "Montreuil": {"lat": 48.8618, "lon": 2.4440, "department": "93", "zone": "Seine-Saint-Denis", "altitude": 82},
        "Bobigny": {"lat": 48.9077, "lon": 2.4174, "department": "93", "zone": "Seine-Saint-Denis", "altitude": 42},
        "Créteil": {"lat": 48.7906, "lon": 2.4550, "department": "94", "zone": "Val-de-Marne", "altitude": 48},
        "Vincennes": {"lat": 48.8483, "lon": 2.4388, "department": "94", "zone": "Val-de-Marne", "altitude": 51},
        "Nogent-sur-Marne": {"lat": 48.8370, "lon": 2.4823, "department": "94", "zone": "Val-de-Marne", "altitude": 39},
        
        # Grande Couronne (77, 78, 91, 95)
        "Versailles": {"lat": 48.8014, "lon": 2.1301, "department": "78", "zone": "Yvelines", "altitude": 132},
        "Saint-Germain-en-Laye": {"lat": 48.9014, "lon": 2.0936, "department": "78", "zone": "Yvelines", "altitude": 78},
        "Cergy-Pontoise": {"lat": 49.0205, "lon": 2.0781, "department": "95", "zone": "Val-d'Oise", "altitude": 30},
        "Roissy-CDG": {"lat": 49.0097, "lon": 2.5479, "department": "95", "zone": "Val-d'Oise", "altitude": 119},
        "Meaux": {"lat": 48.9559, "lon": 2.8781, "department": "77", "zone": "Seine-et-Marne", "altitude": 51},
        "Fontainebleau": {"lat": 48.4020, "lon": 2.7019, "department": "77", "zone": "Seine-et-Marne", "altitude": 115},
        "Evry": {"lat": 48.6247, "lon": 2.4437, "department": "91", "zone": "Essonne", "altitude": 78},
        "Orly": {"lat": 48.7436, "lon": 2.4090, "department": "94", "zone": "Val-de-Marne", "altitude": 89}
    }
    
    # Conditions météo typiques d'Île-de-France
    weather_conditions = [
        "clear", "partly_cloudy", "cloudy", "overcast", 
        "light_rain", "moderate_rain", "drizzle", 
        "thunderstorm", "fog", "mist", "haze",
        "light_snow", "snow"  # Plus rare
    ]
    
    # Directions du vent dominantes en Île-de-France
    wind_directions = ["SW", "W", "NW", "S", "WSW", "SSW", "NE", "E"]
    
    # Types de pollution atmosphérique
    pollutants = ["PM10", "PM2.5", "NO2", "O3", "SO2", "CO"]
    
    for _ in range(num_readings):
        # Sélection aléatoire d'une station
        station_name = random.choice(list(weather_stations.keys()))
        station_info = weather_stations[station_name]
        
        # Timestamp récent (dernières 72h pour avoir plus de variété)
        timestamp = datetime.datetime.now() - datetime.timedelta(minutes=random.randint(0, 72*60))
        
        # Température réaliste pour l'Île-de-France selon la saison
        season_temps = {
            "winter": {"base": 5, "min": -5, "max": 12},    # Déc-Fév
            "spring": {"base": 12, "min": 5, "max": 20},    # Mar-Mai
            "summer": {"base": 22, "min": 15, "max": 35},   # Jun-Aoû
            "autumn": {"base": 12, "min": 5, "max": 18}     # Sep-Nov
        }
        
        month = timestamp.month
        if month in [12, 1, 2]:
            season = "winter"
        elif month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        else:
            season = "autumn"
        
        season_data = season_temps[season]
        
        # Variation selon l'heure (amplitude thermique diurne)
        hour_factor = math.sin((timestamp.hour - 6) * math.pi / 12) * 4
        
        # Effet d'îlot de chaleur urbain (Paris plus chaud que banlieue)
        urban_heat_island = 2 if station_info["zone"] == "Paris" else 0
        
        temperature = round(
            season_data["base"] + hour_factor + urban_heat_island + 
            random.uniform(-3, 3), 1
        )
        
        # Humidité relative (%) - plus élevée en hiver
        base_humidity = 75 if season == "winter" else 65
        humidity = min(95, max(30, base_humidity + random.randint(-20, 20)))
        
        # Pression atmosphérique (hPa) - ajustée selon l'altitude
        base_pressure = 1013.25 - (station_info["altitude"] * 0.12)
        pressure = round(base_pressure + random.uniform(-15, 15), 1)
        
        # Vitesse du vent (km/h) - généralement modéré en IdF
        wind_speed = round(random.uniform(2, 25), 1)
        wind_direction = random.choice(wind_directions)
        
        # Conditions météo avec probabilités réalistes
        condition_weights = {
            "cloudy": 0.25, "partly_cloudy": 0.20, "overcast": 0.15,
            "light_rain": 0.12, "clear": 0.10, "drizzle": 0.08,
            "mist": 0.05, "moderate_rain": 0.03, "fog": 0.015,
            "thunderstorm": 0.005, "light_snow": 0.003 if season == "winter" else 0.001
        }
        weather_condition = random.choices(
            list(condition_weights.keys()), 
            weights=list(condition_weights.values())
        )[0]
        
        # Précipitations
        if "rain" in weather_condition:
            precipitation = round(random.uniform(0.1, 8.0), 1)
        elif weather_condition == "drizzle":
            precipitation = round(random.uniform(0.1, 1.5), 1)
        elif "snow" in weather_condition:
            precipitation = round(random.uniform(0.1, 5.0), 1)
        else:
            precipitation = 0.0
        
        # Visibilité selon les conditions
        visibility_map = {
            "fog": random.uniform(0.1, 1.0),
            "mist": random.uniform(1.0, 8.0),
            "moderate_rain": random.uniform(3.0, 8.0),
            "light_rain": random.uniform(8.0, 15.0),
            "default": random.uniform(15.0, 35.0)
        }
        visibility = round(visibility_map.get(weather_condition, visibility_map["default"]), 1)
        
        # Index UV
        uv_index = 0
        if 7 <= timestamp.hour <= 17:
            if weather_condition in ["clear", "partly_cloudy"]:
                uv_index = random.randint(2, 8) if season == "summer" else random.randint(1, 4)
            else:
                uv_index = random.randint(0, 2)
        
        # Point de rosée
        dew_point = round(temperature - ((100 - humidity) / 5), 1)
        
        # Sensation thermique avec facteur vent
        feels_like = round(temperature - (wind_speed * 0.15) if wind_speed > 10 else temperature, 1)
        
        # Qualité de l'air et polluants (problématique en IdF)
        air_quality_index = random.choices([1, 2, 3, 4, 5], weights=[0.1, 0.3, 0.4, 0.15, 0.05])[0]
        air_quality_levels = ["Bon", "Moyen", "Dégradé", "Mauvais", "Très mauvais"]
        
        # Concentrations de polluants (μg/m³)
        pollutant_data = {}
        for pollutant in pollutants:
            if pollutant == "PM10":
                pollutant_data[pollutant] = random.randint(10, 80)
            elif pollutant == "PM2.5":
                pollutant_data[pollutant] = random.randint(5, 50)
            elif pollutant == "NO2":
                pollutant_data[pollutant] = random.randint(15, 120)
            elif pollutant == "O3":
                pollutant_data[pollutant] = random.randint(20, 180)
            elif pollutant == "SO2":
                pollutant_data[pollutant] = random.randint(1, 20)
            elif pollutant == "CO":
                pollutant_data[pollutant] = random.randint(200, 2000)
        
        weather_reading = {
            "reading_id": f"PAR-{str(uuid.uuid4())[:8]}",
            "timestamp": timestamp.isoformat() + "Z",
            "station": {
                "name": station_name,
                "coordinates": {
                    "latitude": station_info["lat"],
                    "longitude": station_info["lon"]
                },
                "department": station_info["department"],
                "zone": station_info["zone"],
                "altitude_m": station_info["altitude"]
            },
            "temperature": {
                "actual_c": temperature,
                "feels_like_c": feels_like,
                "dew_point_c": dew_point,
                "urban_heat_island_effect": urban_heat_island
            },
            "atmospheric": {
                "humidity_percent": humidity,
                "pressure_hpa": pressure,
                "visibility_km": visibility
            },
            "wind": {
                "speed_kmh": wind_speed,
                "direction": wind_direction,
                "gust_kmh": round(wind_speed * random.uniform(1.2, 1.6), 1) if wind_speed > 8 else wind_speed
            },
            "precipitation": {
                "amount_mm": precipitation,
                "type": "rain" if "rain" in weather_condition else "snow" if "snow" in weather_condition else "none",
                "intensity": "light" if precipitation < 2.5 else "moderate" if precipitation < 7.5 else "heavy"
            },
            "conditions": {
                "weather": weather_condition,
                "description": weather_condition.replace("_", " ").title(),
                "uv_index": uv_index,
                "season": season
            },
            "air_quality": {
                "overall_index": air_quality_index,
                "overall_description": air_quality_levels[air_quality_index - 1],
                "pollutants": pollutant_data
            },
            "metadata": {
                "data_source": "paris_weather_network",
                "region": "Île-de-France",
                "measurement_height_m": 2,  # Hauteur standard des capteurs
                "quality_control": {
                    "temperature_valid": -20 <= temperature <= 45,
                    "pressure_valid": 950 <= pressure <= 1050,
                    "humidity_valid": 0 <= humidity <= 100,
                    "wind_valid": wind_speed <= 150,
                    "precipitation_valid": precipitation < 100
                }
            }
        }
        
        weather_readings.append(weather_reading)
    
    return weather_readings

# Fonction qui envoie des messages dans Kafka
def send_paris_weather_messages(thread_id, num_messages, sleep_time=2):
    """Envoie les données météo d'Île-de-France vers Kafka."""
    readings = generate_paris_weather_data(num_messages)
    
    for reading_number, reading in enumerate(readings):
        # Ajout d'infos sur le thread et traitement
        reading["thread_id"] = thread_id
        reading["message_number"] = reading_number
        reading["processing_timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # Envoi vers Kafka avec clé de partition (station)
            station_key = reading["station"]["name"]
            future = producer.send(
                topic_name, 
                key=station_key.encode('utf-8'),
                value=reading
            )
            result = future.get(timeout=10)
            
            station_name = reading["station"]["name"]
            temp = reading["temperature"]["actual_c"]
            condition = reading["conditions"]["description"]
            zone = reading["station"]["zone"]
            air_quality = reading["air_quality"]["overall_description"]
            
            print(f"🌤️  Thread {thread_id} - Message {reading_number}: "
                  f"{station_name} ({zone}) | "
                  f"{temp}°C | {condition} | "
                  f"Air: {air_quality}")
            
        except Exception as e:
            print(f"❌ Erreur Thread {thread_id} - Message {reading_number}: {e}")
        
        time.sleep(sleep_time)

if __name__ == '__main__':
    print("🚀 Démarrage du producteur de données météo Paris/Île-de-France...")
    
    # Configuration du producer Kafka
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=json_serializer,
        key_serializer=lambda x: x,  # Pour les clés de partition
        acks='all',
        retries=3,
        max_in_flight_requests_per_connection=1,
        request_timeout_ms=30000
    )
    
    # Test de connexion
    try:
        metadata = producer.bootstrap_connected()
        print(f"✅ Connecté à Kafka - Topic: {topic_name}")
    except Exception as e:
        print(f"❌ Échec de connexion à Kafka: {e}")
        exit(1)
    
    # Configuration des threads
    threads = []
    num_threads = 3  # 3 threads pour simuler 3 sources de données
    num_messages = 50  # 15 messages par thread = 45 stations au total
    sleep_time = 1.5   # 1.5 secondes entre chaque envoi
    
    print(f"📊 Configuration: {num_threads} threads × {num_messages} messages = {num_threads * num_messages} relevés météo")
    print(f"⏱️  Intervalle: {sleep_time}s entre chaque envoi")
    print(f"🗺️  Couverture: Paris (20 arr.) + Petite/Grande Couronne")
    print("─" * 80)
    
    # Création et démarrage des threads
    for i in range(num_threads):
        thread = threading.Thread(
            target=send_paris_weather_messages, 
            args=(i, num_messages, sleep_time)
        )
        threads.append(thread)
        thread.start()
        print(f"🔄 Thread {i} démarré...")
    
    # Attente de la fin de tous les threads
    for thread in threads:
        thread.join()
    
    # Fermeture propre du producer
    producer.flush()
    producer.close()
    
    print("─" * 80)
    print("✅ Tous les messages météo ont été envoyés avec succès !")
    print(f"📈 Vérifiez les données dans Control Center: http://localhost:9021")
    print(f"🔍 Topic Kafka: {topic_name}")
