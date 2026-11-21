#!/usr/bin/env bash
# ==============================================================================
# TaskFlow Deployment Script (Point 6 & Bonus 2)
# Conforms to DevOps Module Standards:
#  - Livrer et mettre en service sur tag vX.Y.Z
#  - Image publiée et JAMAIS reconstruite en déploiement
#  - Contrôle de santé systématique sur /health
# ==============================================================================

set -eo pipefail

TAG="${1:-}"

if [ -z "$TAG" ]; then
    echo "❌ Usage: $0 <vX.Y.Z> (e.g., $0 v1.0.0)"
    exit 1
fi

echo "=========================================================="
echo " 🚀 Deploying TaskFlow Release: ${TAG}                     "
echo "=========================================================="

export IMAGE_TAG="$TAG"

# Step 1: Start container services using the pre-built image tag
echo "[1/3] Launching application & database containers with image tag ${IMAGE_TAG}..."
docker compose up -d

# Step 2: Wait for services and healthcheck readiness
echo "[2/3] Awaiting container healthcheck convergence..."
MAX_RETRIES=15
COUNTER=0
HEALTHY=0

while [ $COUNTER -lt $MAX_RETRIES ]; do
    COUNTER=$((COUNTER+1))
    echo "  Checking health (attempt $COUNTER/$MAX_RETRIES)..."
    
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        HEALTHY=1
        break
    fi
    sleep 3
done

if [ $HEALTHY -eq 0 ]; then
    echo "❌ Deployment failed: Healthcheck endpoint did not respond with 200 OK!"
    echo "Showing container logs:"
    docker compose logs app --tail 30
    exit 1
fi

# Step 3: Success output
echo "=========================================================="
echo " ✅ DEPLOYMENT SUCCESSFUL for ${IMAGE_TAG}                  "
echo " Service is LIVE and HEALTHY at http://localhost:8000      "
echo "=========================================================="
exit 0
