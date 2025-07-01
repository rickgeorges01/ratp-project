#!/bin/bash

# Script de démarrage de l'infrastructure RATP avec gestion des erreurs

set -e  # Arrêt en cas d'erreur

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher des messages colorés
log_info() {
    echo -e "${BLUE}$1${NC}"
}

log_success() {
    echo -e "${GREEN}$1${NC}"
}

log_warning() {
    echo -e "${YELLOW}$1${NC}"
}

log_error() {
    echo -e "${RED}$1${NC}"
}

# Fonction pour vérifier si un service est prêt
check_service() {
    local service_name=$1
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker compose -f docker-compose.infra.yml ps | grep -q "$service_name.*Up"; then
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    return 1
}

# Header
echo "🚀 Démarrage de l'infrastructure RATP..."

# Arrêt des services existants
log_info "🛑 Arrêt des services existants..."
docker compose -f docker-compose.infra.yml -f docker-compose.dev.yml down --remove-orphans

# Création du réseau si nécessaire
docker network create ratp-network 2>/dev/null || true

# Démarrage de l'infrastructure de base
log_info "📦 Démarrage de l'infrastructure (Kafka, MinIO, Spark)..."
docker compose -f docker-compose.infra.yml up -d --remove-orphans

# Attente du démarrage des services critiques
log_info "⏳ Attente du démarrage de l'infrastructure (10 secondes)..."
sleep 10

# Démarrage du producteur de données
log_info "📊 Démarrage du producteur de données..."
docker compose -f docker-compose.infra.yml -f docker-compose.dev.yml up -d data-producer

# Démarrage du job Spark Streaming avec rebuild sans cache
log_info "⚡ Démarrage du job Spark Streaming..."
docker compose -f docker-compose.infra.yml -f docker-compose.dev.yml build --no-cache spark-streaming
docker compose -f docker-compose.infra.yml -f docker-compose.dev.yml up -d spark-streaming

# Démarrage du dashboard Streamlit
log_info "📈 Démarrage du dashboard Streamlit..."
docker compose -f docker-compose.infra.yml -f docker-compose.dev.yml --profile dashboard up -d

# Vérification finale
sleep 5
log_success "✅ Tous les services sont démarrés !"

# Affichage des URLs
echo ""
log_info "🌐 Accès aux interfaces :"
echo "  - Kafka UI: http://localhost:8080"
echo "  - MinIO Console: http://localhost:9001 (minioadmin / minioadmin123)"
echo "  - Spark Master UI: http://localhost:8082"
echo "  - Spark Worker UI: http://localhost:8083"
echo "  - Streamlit Dashboard: http://localhost:8501"

echo ""
log_info "📋 Pour voir les logs :"
echo "  docker compose -f docker-compose.infra.yml -f docker-compose.dev.yml logs -f [service-name]"

echo ""
log_info "🛑 Pour arrêter tous les services :"
echo "  docker compose -f docker-compose.infra.yml -f docker-compose.dev.yml down"