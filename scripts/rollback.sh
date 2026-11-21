#!/usr/bin/env bash
# ==============================================================================
# TaskFlow Automated Rollback Script (Point 7)
# Conforms to DevOps Module Standards:
#  - Retour à la version précédente démontré
#  - Bascule vers l'image du tag spécifié SANS reconstruction
#  - Contrôle de santé après rollback
# ==============================================================================

set -eo pipefail

TARGET_TAG="${1:-}"

if [ -z "$TARGET_TAG" ]; then
    echo "❌ Usage: $0 <previous_tag> (e.g., $0 v0.9.0)"
    echo "Please specify the previous version tag to roll back to."
    exit 1
fi

echo "=========================================================="
echo " ⚠️  INITIATING ROLLBACK TO VERSION: ${TARGET_TAG}        "
echo "=========================================================="

# Step 1: Update environment variable without touching source code
export IMAGE_TAG="$TARGET_TAG"

echo "[1/3] Switching container deployment to previous image: taskflow:${IMAGE_TAG}..."
# Deploy previous image tag without rebuild
docker compose up -d --no-build app

# Step 2: Validate healthcheck of the restored version
echo "[2/3] Verifying service health after rollback..."
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
    sleep 2
done

if [ $HEALTHY -eq 0 ]; then
    echo "❌ Rollback verification failed: Application did not recover healthy state!"
    docker compose logs app --tail 30
    exit 1
fi

# Step 3: Success Confirmation
echo "=========================================================="
echo " ✅ ROLLBACK COMPLETED SUCCESSFULLY                        "
echo " Currently running version: ${TARGET_TAG}                  "
echo " Healthcheck confirmed: http://localhost:8000/health (200) "
echo "=========================================================="
exit 0
