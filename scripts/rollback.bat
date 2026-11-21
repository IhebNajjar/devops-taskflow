@echo off
set TARGET_TAG=%1
if "%TARGET_TAG%"=="" (
    echo [ERROR] Usage: rollback.bat ^<previous_tag^> (e.g. rollback.bat v0.9.0)
    exit /b 1
)

echo ==========================================================
echo  [DevOps Rollback] Rolling back to version: %TARGET_TAG%
echo ==========================================================

set IMAGE_TAG=%TARGET_TAG%
echo [1/2] Rolling back container WITHOUT rebuild (--no-build)...
docker compose up -d --no-build app

echo [2/2] Checking health of restored version...
timeout /t 2 /nobreak >nul
python -c "import urllib.request; res = urllib.request.urlopen('http://localhost:8000/health'); assert res.getcode() == 200; print('HEALTH CHECK PASSED: 200 OK')"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Rollback healthcheck failed!
    exit /b 1
)

echo ==========================================================
echo  [SUCCESS] Rollback to %TARGET_TAG% completed successfully!
echo  Application is running and healthy at http://localhost:8000
echo ==========================================================
exit /b 0
