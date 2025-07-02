#!/bin/bash

# RATP Infrastructure Setup - MVP Version
set -e

echo " Starting RATP infrastructure..."

# 1. Vérifier que Docker est actif
if ! docker info &> /dev/null; then
    echo "ERROR: Docker is not running"
    exit 1
fi

# 2. Vérifier présence du .env
if [ ! -f .env ]; then
    echo "ERROR: .env file not found in current directory"
    exit 1
fi

# 3. Nettoyage
echo "🧹 Cleaning up old containers..."
docker compose -f docker-compose.infra.yml down -v --remove-orphans || true
docker network rm ratp-network 2>/dev/null || true

# 4. Lancer l’infrastructure
echo "Starting services..."
docker network create ratp-network || true
docker compose -f docker-compose.infra.yml up -d

# 5. Attente active de chaque composant

wait_for_service() {
    local name="$1"
    local url="$2"
    local max_attempts="$3"
    local delay="$4"

    echo -n "Waiting for $name"
    for i in $(seq 1 "$max_attempts"); do
        if curl -s "$url" > /dev/null 2>&1; then
            echo " ✓"
            return 0
        fi
        echo -n "."
        sleep "$delay"
    done
    echo " ✗"
    echo "ERROR: $name did not respond at $url after ${max_attempts} tries."
    exit 1
}

echo ""
wait_for_service "MinIO Console" "http://localhost:9001" 30 2
wait_for_service "Control Center" "http://localhost:9021" 60 3
wait_for_service "Spark UI" "http://localhost:8082" 20 2

# Test Kafka en interne (kafka-1:29092)
echo -n "Waiting for Kafka Broker"
for i in {1..30}; do
    if docker exec ratp-kafka-1 kafka-topics --bootstrap-server kafka-1:29092 --list &>/dev/null; then
        echo " ✓"
        break
    fi
    echo -n "."
    sleep 2
    if [ "$i" -eq 30 ]; then
        echo " ✗"
        echo "ERROR: Kafka broker not responding inside container"
        exit 1
    fi
done

# 6. Lancer les scripts si demandé
if [[ "$1" == "--full" ]]; then
    echo "Launching application services (batch + streaming)"
    docker-compose -f docker compose.dev.yml --profile batch up -d
    echo "🟢 Scripts de traitement en cours..."
fi

# 7. Résumé
echo ""
echo "Infrastructure is ready!"
echo "Access points:"
echo "- MinIO Console:     http://localhost:9001"
echo "- Kafka Control:     http://localhost:9021"
echo "- Spark Master:      http://localhost:8082"
echo ""
echo "Next step (manual):"
echo "docker compose -f docker-compose.dev.yml --profile batch up"
echo ""
