FROM python:3.11-slim
LABEL authors="YELEUMEU-CHRISTYRAS-WAHBA-GUELAI"

WORKDIR /app

# Installation dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY . .

# Variables d'environnement
ENV MINIO_ENDPOINT=http://minio:9000
ENV MINIO_ACCESS_KEY=minioadmin
ENV MINIO_SECRET_KEY=minioadmin123

# Port Streamlit
EXPOSE 8501

# Point d'entrée
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]