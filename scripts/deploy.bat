@echo off
set TAG=%1
if "%TAG%"=="" (
    echo [ERROR] Usage: deploy.bat ^<vX.Y.Z^> (e.g. deploy.bat v1.0.0)
    exit /b 1
)

echo ==========================================================
echo  [DevOps Deploy] Deploying Release: %TAG%
echo ==========================================================

set IMAGE_TAG=%TAG%
echo [1/2] Starting containers with image tag: %IMAGE_TAG%...
docker compose up -d

echo [2/2] Checking application health at http://localhost:8000/health...
timeout /t 3 /nobreak >nul
python -c "import urllib.request; res = urllib.request.urlopen('http://localhost:8000/health'); assert res.getcode() == 200; print('HEALTH CHECK PASSED: 200 OK')"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Healthcheck failed!
    exit /b 1
)

echo ==========================================================
echo  [SUCCESS] Deployment of %TAG% completed successfully!
echo ==========================================================
exit /b 0
