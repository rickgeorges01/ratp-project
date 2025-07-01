#!/bin/bash

# RATP Infrastructure Setup - MVP Version
set -e

echo "Starting RATP infrastructure..."

# Check Docker running
if ! docker info &> /dev/null; then
    echo "ERROR: Docker not running"
    exit 1
fi

# Cleanup existing
echo "Cleaning up..."
docker-compose -f docker-compose.infra.yml down -v 2>/dev/null || true
docker network rm ratp-network 2>/dev/null || true

# Start infrastructure
echo "Starting services..."
docker network create ratp-network || true
docker-compose -f docker-compose.infra.yml up -d

# Health checks with loops
echo "Waiting for services..."

# Wait for MinIO
echo -n "MinIO"
for i in {1..30}; do
    if curl -s http://localhost:9001 > /dev/null 2>&1; then
        echo " ✓"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Kafka
echo -n "Kafka"
for i in {1..30}; do
    if docker exec ratp-kafka-1 kafka-topics --bootstrap-server localhost:9092 --list &>/dev/null; then
        echo " ✓"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Spark
echo -n "Spark"
for i in {1..20}; do
    if curl -s http://localhost:8082 > /dev/null 2>&1; then
        echo " ✓"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Control Center (takes longest)
echo -n "Control Center"
for i in {1..60}; do
    if curl -s http://localhost:9021 > /dev/null 2>&1; then
        echo " ✓"
        break
    fi
    echo -n "."
    sleep 3
done

# Show status
echo ""
echo "Infrastructure status:"
docker-compose -f docker-compose.infra.yml ps

echo ""
echo "Ready! Access points:"
echo "- Control Center: http://localhost:9021"
echo "- MinIO Console: http://localhost:9001"
echo "- Spark Master: http://localhost:8082"
echo ""
echo "Next: docker-compose -f docker-compose.dev.yml --profile batch up"