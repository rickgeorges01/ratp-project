FROM bitnami/spark:3.5.1
LABEL authors="YELEUMEU-CHRISTYRAS-WAHBA-GUELAI"

USER root

# Installation Python packages
RUN pip3 install kafka-python boto3 pandas scikit-learn

# Copie du code
COPY . /app
WORKDIR /app

# Permissions - Utiliser l'utilisateur Bitnami (1001)
RUN chown -R 1001:1001 /app

# Retour à l'utilisateur non-root Bitnami
USER 1001

# Variables d'environnement
ENV SPARK_MASTER_URL=spark://spark-master:7077
ENV KAFKA_BOOTSTRAP_SERVERS=kafka:29092

# Point d'entrée
CMD ["python", "streaming_job.py"]