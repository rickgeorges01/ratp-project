FROM python:3.11-slim
LABEL authors="YELEUMEU-CHRISTYRAS-WAHBA-GUELAI"

WORKDIR /app

# Installation dépendances minimales
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY . .

# Variables d'environnement
ENV KAFKA_BOOTSTRAP_SERVERS=kafka:29092
ENV STATION=auber
ENV SEND_INTERVAL=30

# Attribution des permissions au nouvel utilisateur
# Basculement vers l'utilisateur non-root


# Point d'entrée
CMD ["python", "producer.py"]