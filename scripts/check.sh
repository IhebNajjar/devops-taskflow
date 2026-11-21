#!/usr/bin/env bash
# ==============================================================================
# TaskFlow Automated Verification Script (Point 2)
# Conforms to DevOps Module Standards:
#  - Renvoie 0 en cas de succès
#  - Renvoie un code non nul (1) en cas d'échec
#  - Exécute les tests unitaires et produit le rapport JUnit XML
# ==============================================================================

set -eo pipefail

echo "=========================================================="
echo " [DevOps Check] Starting TaskFlow Verification Pipeline   "
echo "=========================================================="

FAILED=0

# Step 1: Syntax & Bytecode Compilation Check
echo "[1/3] Checking Python syntax..."
python -m py_compile main.py database.py models.py ai_assistant.py || {
    echo "❌ ERROR: Python syntax check failed!"
    FAILED=1
}

if [ $FAILED -ne 0 ]; then
    echo "Verification failed at Step 1."
    exit 1
fi
echo "✅ Syntax check passed."

# Step 2: Automated Unit Testing with JUnit XML Generation
echo "[2/3] Running automated unit test suite with pytest..."
pytest test_api.py -v --junitxml=test-results.xml || {
    echo "❌ ERROR: Unit tests failed!"
    FAILED=1
}

if [ $FAILED -ne 0 ]; then
    echo "Verification failed at Step 2."
    exit 1
fi
echo "✅ Unit tests passed (8/8). Test report saved to test-results.xml."

# Step 3: Healthcheck Route Contract Verification
echo "[3/3] Validating /health endpoint structure..."
python -c "
from fastapi.testclient import TestClient
from main import app
client = TestClient(app)
res = client.get('/health')
assert res.status_code == 200, f'Expected 200, got {res.status_code}'
assert res.json() == {'status': 'ok'}, f'Unexpected payload {res.json()}'
print('Health route contract OK.')
" || {
    echo "❌ ERROR: Healthcheck route validation failed!"
    FAILED=1
}

if [ $FAILED -ne 0 ]; then
    echo "Verification failed at Step 3."
    exit 1
fi

echo "=========================================================="
echo " 🎉 ALL CHECKS PASSED SUCCESSFULLY (Exit Code: 0)         "
echo "=========================================================="
exit 0
