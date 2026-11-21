@echo off
echo ==========================================================
echo  [DevOps Check] Starting TaskFlow Verification (Windows)
echo ==========================================================

echo [1/3] Checking Python syntax...
python -m py_compile main.py database.py models.py ai_assistant.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Syntax check failed!
    exit /b 1
)
echo [OK] Syntax check passed.

echo [2/3] Running pytest unit test suite...
pytest test_api.py -v --junitxml=test-results.xml
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Unit tests failed!
    exit /b 1
)
echo [OK] Unit tests passed. Test report written to test-results.xml.

echo [3/3] Validating /health route...
python -c "from fastapi.testclient import TestClient; from main import app; client = TestClient(app); res = client.get('/health'); assert res.status_code == 200 and res.json() == {'status': 'ok'}"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Health route check failed!
    exit /b 1
)
echo [OK] Health contract verified.

echo ==========================================================
echo  [SUCCESS] ALL CHECKS PASSED (Exit Code: 0)
echo ==========================================================
exit /b 0
