FROM python:3.11-slim

# Installer les outils nécessaires + Java 17 de manière plus robuste
RUN apt-get update -o Acquire::Retries=5 && \
    apt-get install -y --no-install-recommends openjdk-17-jdk curl procps && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Définir JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "batch_producer.py"]
