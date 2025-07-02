"""
 Simulation météo réaliste
"""
import random
import datetime
import uuid
import math


def generate_paris_weather_data(num_readings=1):
    """Génère des données météo réalistes pour Paris + Île-de-France."""

    weather_stations = {
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
    }

    weather_conditions = [
        "clear", "partly_cloudy", "cloudy", "overcast",
        "light_rain", "moderate_rain", "drizzle",
        "thunderstorm", "fog", "mist", "haze",
        "light_snow", "snow"
    ]

    wind_directions = ["SW", "W", "NW", "S", "WSW", "SSW", "NE", "E"]
    pollutants = ["PM10", "PM2.5", "NO2", "O3", "SO2", "CO"]

    season_temps = {
        "winter": {"base": 5, "min": -5, "max": 12},
        "spring": {"base": 12, "min": 5, "max": 20},
        "summer": {"base": 22, "min": 15, "max": 35},
        "autumn": {"base": 12, "min": 5, "max": 18}
    }

    readings = []

    for _ in range(num_readings):
        station_name = random.choice(list(weather_stations.keys()))
        station_info = weather_stations[station_name]
        timestamp = datetime.datetime.now() - datetime.timedelta(minutes=random.randint(0, 72 * 60))

        # Saison
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
        hour_factor = math.sin((timestamp.hour - 6) * math.pi / 12) * 4
        urban_heat_island = 2 if station_info["zone"] == "Paris" else 0

        temperature = round(
            season_data["base"] + hour_factor + urban_heat_island +
            random.uniform(-3, 3), 1
        )

        humidity = min(95, max(30, 65 + random.randint(-20, 20)))
        base_pressure = 1013.25 - (station_info["altitude"] * 0.12)
        pressure = round(base_pressure + random.uniform(-15, 15), 1)
        wind_speed = round(random.uniform(2, 25), 1)
        wind_direction = random.choice(wind_directions)

        condition_weights = {
            "cloudy": 0.25, "partly_cloudy": 0.20, "overcast": 0.15,
            "light_rain": 0.12, "clear": 0.10, "drizzle": 0.08,
            "mist": 0.05, "moderate_rain": 0.03, "fog": 0.015,
            "thunderstorm": 0.005, "light_snow": 0.003 if season == "winter" else 0.001
        }
        weather_condition = random.choices(list(condition_weights.keys()), weights=list(condition_weights.values()))[0]

        if "rain" in weather_condition:
            precipitation = round(random.uniform(0.1, 8.0), 1)
        elif weather_condition == "drizzle":
            precipitation = round(random.uniform(0.1, 1.5), 1)
        elif "snow" in weather_condition:
            precipitation = round(random.uniform(0.1, 5.0), 1)
        else:
            precipitation = 0.0

        visibility_map = {
            "fog": random.uniform(0.1, 1.0),
            "mist": random.uniform(1.0, 8.0),
            "moderate_rain": random.uniform(3.0, 8.0),
            "light_rain": random.uniform(8.0, 15.0),
            "default": random.uniform(15.0, 35.0)
        }
        visibility = round(visibility_map.get(weather_condition, visibility_map["default"]), 1)

        uv_index = 0
        if 7 <= timestamp.hour <= 17:
            if weather_condition in ["clear", "partly_cloudy"]:
                uv_index = random.randint(2, 8) if season == "summer" else random.randint(1, 4)
            else:
                uv_index = random.randint(0, 2)

        dew_point = round(temperature - ((100 - humidity) / 5), 1)
        feels_like = round(temperature - (wind_speed * 0.15) if wind_speed > 10 else temperature, 1)

        air_quality_index = random.choices([1, 2, 3, 4, 5], weights=[0.1, 0.3, 0.4, 0.15, 0.05])[0]
        air_quality_levels = ["Bon", "Moyen", "Dégradé", "Mauvais", "Très mauvais"]

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

        readings.append({
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
                "direction": wind_direction
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
                "measurement_height_m": 2,
                "quality_control": {
                    "temperature_valid": -20 <= temperature <= 45,
                    "pressure_valid": 950 <= pressure <= 1050,
                    "humidity_valid": 0 <= humidity <= 100,
                    "wind_valid": wind_speed <= 150,
                    "precipitation_valid": precipitation < 100
                }
            }
        })

    return readings
