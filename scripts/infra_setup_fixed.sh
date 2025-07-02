#!/bin/bash
# RATP Infrastructure Setup - FIXED VERSION
set -e

echo "🚀 Starting RATP infrastructure (FIXED)..."

# Couleurs pour les logs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction de log
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check Docker running
if ! docker info &> /dev/null; then
    error "Docker not running. Please start Docker first."
    exit 1
fi

log "✅ Docker is running"

# Create required directories
log "📁 Creating required directories..."
mkdir -p spark-apps
mkdir -p data
mkdir -p logs

# Cleanup existing (with proper error handling)
log "🧹 Cleaning up existing containers..."
docker compose -f docker-compose.infra-fixed.yml down 2>/dev/null || true

# Clean up network properly
log "🌐 Managing network..."
if docker network ls | grep -q ratp-network; then
    warning "Network ratp-network already exists - removing and recreating..."
    # Stop any containers using the network first
    docker network disconnect ratp-network $(docker network inspect ratp-network -f '{{range .Containers}}{{.Name}} {{end}}') 2>/dev/null || true
    docker network rm ratp-network 2>/dev/null || true
fi

# Create clean network
docker network create ratp-network
log "✅ Network ratp-network created"

# Start core services first (staged deployment)
log "📦 Stage 1: Starting Zookeeper..."
docker compose -f docker-compose.infra-fixed.yml up -d zookeeper

log "⏳ Waiting for Zookeeper (15s)..."
sleep 15

log "📦 Stage 2: Starting Kafka cluster..."
docker compose -f docker-compose.infra-fixed.yml up -d kafka-1 kafka-2

log "⏳ Waiting for Kafka cluster (20s)..."
sleep 20

log "📦 Stage 3: Starting MinIO and setup..."
docker compose -f docker-compose.infra-fixed.yml up -d minio minio-setup

log "⏳ Waiting for MinIO (15s)..."
sleep 15

log "📦 Stage 4: Starting Spark cluster..."
docker compose -f docker-compose.infra-fixed.yml up -d spark-master spark-worker-1 spark-worker-2

log "⏳ Waiting for Spark (15s)..."
sleep 15

log "📦 Stage 5: Starting Control Center..."
docker compose -f docker-compose.infra-fixed.yml up -d control-center

# Health checks with improved feedback
log "🔍 Running health checks..."

# Wait for MinIO
echo -n "MinIO Console"
for i in {1..30}; do
    if curl -s http://localhost:9001 > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Kafka
echo -n "Kafka Cluster"
for i in {1..30}; do
    if docker exec ratp-kafka-1 kafka-topics --bootstrap-server localhost:9092 --list &>/dev/null; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Spark
echo -n "Spark Master"
for i in {1..20}; do
    if curl -s http://localhost:8082 > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Control Center (takes longest)
echo -n "Control Center"
for i in {1..60}; do
    if curl -s http://localhost:9021 > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 3
done

# Show final status
echo ""
log "📊 Infrastructure status:"
docker compose -f docker-compose.infra-fixed.yml ps

# Show container health
echo ""
log "🏥 Container health:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep ratp

echo ""
log "🎉 Ready! Access points:"
echo -e "   🌐 Control Center: ${GREEN}http://localhost:9021${NC}"
echo -e "   ☁️  MinIO Console:  ${GREEN}http://localhost:9001${NC} (minioadmin/minioadmin123)"
echo -e "   ⚡ Spark Master:   ${GREEN}http://localhost:8082${NC}"
echo -e "   👨‍💻 Spark Worker 1: ${GREEN}http://localhost:8083${NC}"
echo -e "   👨‍💻 Spark Worker 2: ${GREEN}http://localhost:8084${NC}"

echo ""
log "📂 MinIO bucket structure created:"
echo "   📦 ratp-raw/weather/streaming/"
echo "   📦 ratp-raw/batch/pm10/"
echo "   📦 ratp-raw/batch/trafic/"
echo "   📦 ratp-raw/data/original/"

echo ""
log "🚀 Next steps:"
echo "   1. Start producers: docker compose -f docker-compose.dev.yml --profile batch up"
echo "   2. Start streaming: docker compose -f docker-compose.dev.yml --profile streaming up"
echo "   3. Start dashboard: docker compose -f docker-compose.dev.yml --profile dashboard up"

# Optional: Show Kafka topics
echo ""
log "📋 Available Kafka topics:"
docker exec ratp-kafka-1 kafka-topics --bootstrap-server localhost:9092 --list 2>/dev/null || echo "   (No topics yet - will be created automatically)"

log "✅ Infrastructure setup complete!"