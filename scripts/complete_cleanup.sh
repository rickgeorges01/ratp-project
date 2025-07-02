#!/bin/bash
# Nettoyage Complet RATP Infrastructure

set -e

# Couleurs pour les logs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

echo "🧹 NETTOYAGE COMPLET DE L'INFRASTRUCTURE RATP"
echo "=============================================="

# Check Docker running
if ! docker info &> /dev/null; then
    error "Docker not running. Please start Docker first."
    exit 1
fi

log "✅ Docker is running"

# 1. Arrêter et supprimer TOUS les containers ratp-*
log "🛑 Arrêt et suppression des containers RATP..."
RATP_CONTAINERS=$(docker ps -a --filter "name=ratp-" --format "{{.Names}}" || true)

if [ ! -z "$RATP_CONTAINERS" ]; then
    info "Containers trouvés:"
    echo "$RATP_CONTAINERS" | sed 's/^/   - /'
    
    # Arrêter d'abord
    echo "$RATP_CONTAINERS" | xargs -r docker stop 2>/dev/null || true
    
    # Puis supprimer
    echo "$RATP_CONTAINERS" | xargs -r docker rm -f 2>/dev/null || true
    
    log "✅ Containers RATP supprimés"
else
    info "Aucun container RATP trouvé"
fi

# 2. Nettoyer avec docker-compose (au cas où)
log "🔄 Nettoyage Docker Compose..."
docker compose -f docker-compose.infra.yml down -v 2>/dev/null || true
docker compose -f docker-compose.infra-fixed.yml down -v 2>/dev/null || true

# 3. Supprimer les volumes RATP spécifiques
log "💾 Nettoyage des volumes RATP..."
RATP_VOLUMES=$(docker volume ls --filter "name=ratp" --format "{{.Name}}" || true)

if [ ! -z "$RATP_VOLUMES" ]; then
    info "Volumes trouvés:"
    echo "$RATP_VOLUMES" | sed 's/^/   - /'
    echo "$RATP_VOLUMES" | xargs -r docker volume rm 2>/dev/null || true
    log "✅ Volumes RATP supprimés"
else
    info "Aucun volume RATP trouvé"
fi

# 4. Gérer le réseau ratp-network
log "🌐 Gestion du réseau..."
if docker network ls | grep -q ratp-network; then
    # Déconnecter tous les containers du réseau
    CONNECTED_CONTAINERS=$(docker network inspect ratp-network -f '{{range .Containers}}{{.Name}} {{end}}' 2>/dev/null | tr ' ' '\n' | grep -v '^$' || true)
    
    if [ ! -z "$CONNECTED_CONTAINERS" ]; then
        warning "Déconnexion des containers du réseau..."
        for container in $CONNECTED_CONTAINERS; do
            docker network disconnect ratp-network $container 2>/dev/null || true
            info "   ✓ $container déconnecté"
        done
    fi
    
    # Supprimer le réseau
    docker network rm ratp-network 2>/dev/null || true
    log "🗑️ Réseau ratp-network supprimé"
fi

# Recréer le réseau
docker network create ratp-network
log "✅ Réseau ratp-network recréé"

# 5. Nettoyer les images inutilisées (optionnel)
if [ "${1}" = "--full" ]; then
    log "🖼️ Nettoyage des images inutilisées..."
    docker image prune -f
fi

# 6. Créer les dossiers nécessaires
log "📁 Création des dossiers requis..."
mkdir -p spark-apps
mkdir -p data
mkdir -p logs

# 7. Vérification finale
log "🔍 Vérification de l'état final..."

# Vérifier qu'aucun container ratp n'existe
REMAINING_CONTAINERS=$(docker ps -a --filter "name=ratp-" --format "{{.Names}}" || true)
if [ -z "$REMAINING_CONTAINERS" ]; then
    log "✅ Aucun container RATP restant"
else
    error "Containers restants: $REMAINING_CONTAINERS"
    exit 1
fi

# Vérifier le réseau
if docker network ls | grep -q ratp-network; then
    log "✅ Réseau ratp-network prêt"
else
    error "Réseau ratp-network non trouvé"
    exit 1
fi

# Vérifier Docker Compose
log "🔧 Validation Docker Compose..."
if docker compose -f docker-compose.infra-fixed.yml config > /dev/null 2>&1; then
    log "✅ Configuration Docker Compose valide"
else
    error "Configuration Docker Compose invalide"
    exit 1
fi

echo ""
echo "🎉 NETTOYAGE TERMINÉ AVEC SUCCÈS !"
echo "=================================="
echo ""
log "🚀 Vous pouvez maintenant démarrer l'infrastructure:"
echo "   docker compose -f docker-compose.infra-fixed.yml up -d"
echo ""
echo "ou utiliser le script:"
echo "   ./infra_setup_fixed.sh"
echo ""

# Option pour démarrer automatiquement
read -p "Voulez-vous démarrer l'infrastructure maintenant ? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "🚀 Démarrage de l'infrastructure..."
    ./infra_setup_fixed.sh
fi