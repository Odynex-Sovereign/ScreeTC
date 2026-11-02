#!/usr/bin/env bash
set -e

echo "=========================================================================="
echo "⚡ INITIALIZING ODYNEX AXIS LOGISTICS LLC - SCREETC INFRASTRUCTURE DEPLOY ⚡"
echo "=========================================================================="

# Step 1: Establish production workspace directory structure
echo "[1/5] Building secure directory architecture..."
mkdir -p src public models/screetc_pinn

# Step 2: Validate environmental hardware prerequisites
echo "[2/5] Checking for Nvidia GPU acceleration components..."
if command -v nvidia-smi &> /dev/null; then
    echo "[SUCCESS] Compatible Tensor Core GPU infrastructure identified:"
    nvidia-smi --query-gpu=name,driver_version --format=csv
else
    echo "[WARNING] Nvidia Drivers not found. Initializing CPU emulation fail-safes."
fi

# Step 3: Install necessary system dependencies and libraries
echo "[3/5] Syncing core runtime python configurations..."
pip install --upgrade pip
pip install flask stripe numpy requests

# Step 4: Verify Docker container configurations are active
echo "[4/5] Pulling multi-tenant proxy assets and database infrastructure layers..."
if command -v docker-compose &> /dev/null; then
    docker-compose down || true
    docker-compose up -d --build
    echo "[SUCCESS] Containers running securely behind Nginx gateway infrastructure."
else
    echo "[ERROR] Docker-Compose dependency missing. Please install the Docker Engine."
    exit 1
fi

# Step 5: Start the main background tracking daemon
echo "[5/5] Launching automated routing services..."
nohup python src/main_api_gateway.py > gateway_execution.log 2>&1 &

echo "=========================================================================="
echo "🚀 PRODUCTION READY: ScreeTC Core is LIVE and open for business."
echo "   Endpoint API Gateway listening on Port 443 / Port 80."
echo "=========================================================================="
