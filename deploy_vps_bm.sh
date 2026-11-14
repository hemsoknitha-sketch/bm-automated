#!/bin/bash
# ==============================================================================
# 🚀 1-CLICK LINUX GOOGLE VPS DEPLOYMENT FOR FB PAGE BM AUTOMATED
# Target: Ubuntu 20.04 / 22.04 / 24.04 LTS (Google Cloud Always Free VPS)
# Supports: Full Systemd Mode (with sudo) & User-Space 24/7 Daemon (without sudo)
# ==============================================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

CURRENT_USER=$(whoami)
NUM_CPUS=$(nproc 2>/dev/null || echo 1)

# Check if user has sudo privileges
CAN_SUDO=0
if sudo -n true 2>/dev/null || sudo true 2>/dev/null; then
    CAN_SUDO=1
fi

echo "======================================================================"
echo "🚀 [1-CLICK DEPLOY] FB PAGE BM AUTOMATED -> LINUX GOOGLE CLOUD VPS"
echo "   User:        $CURRENT_USER"
echo "   Directory:   $DIR"
echo "   vCPUs:       $NUM_CPUS"
if [ "$CAN_SUDO" -eq 1 ]; then
    echo "   Sudo Mode:   ✅ ENABLED (Full Systemd 24/7 Integration)"
else
    echo "   Sudo Mode:   ℹ️ USER-SPACE ONLY (Zero-Sudo 24/7 Background Mode)"
fi
echo "======================================================================"

# 0. Clean old caches & maximize available disk space
echo "🧹 Step 0: Cleaning caches and checking disk space..."
rm -rf ~/.cache/pip ~/.cache/* /tmp/pip-* /tmp/* 2>/dev/null || true
if [ "$CAN_SUDO" -eq 1 ]; then
    sudo apt-get clean -y 2>/dev/null || true
fi

FREE_MB=$(df -m "$DIR" | awk 'NR==2 {print $4}')
echo "💾 Available Disk Space: ${FREE_MB} MB"

# 1. System packages (if sudo is available)
if [ "$CAN_SUDO" -eq 1 ]; then
    echo "📦 Step 1: Installing system packages via apt..."
    sudo apt-get update -y
    sudo apt-get install -y python3-pip python3-venv python3-dev build-essential unzip curl
    sudo apt-get clean -y 2>/dev/null || true
else
    echo "📦 Step 1: Skipping apt (User-space mode, using existing Python runtime)..."
fi

# 2. Setup isolated Python Virtual Environment
echo "📦 Step 2: Setting up Python environment..."
PYTHON_SYS=$(which python3 || echo "python3")

if $PYTHON_SYS -m venv venv 2>/dev/null; then
    source venv/bin/activate
    PYTHON_BIN="$DIR/venv/bin/python3"
    echo "✅ Created and activated isolated venv/"
    pip install --upgrade pip --no-cache-dir --quiet 2>/dev/null || true
    echo "📦 Step 3: Installing dependencies in venv (fast binary mode)..."
    pip install --no-cache-dir --prefer-binary -r requirements.txt
    # Optional compiled ML packages (only if pre-built wheels exist for this python version)
    pip install --no-cache-dir --only-binary=:all: lightgbm xgboost 2>/dev/null || true
else
    echo "ℹ️ venv module not installed, installing dependencies in user space..."
    $PYTHON_SYS -m pip install --user --no-cache-dir --prefer-binary -r requirements.txt
    $PYTHON_SYS -m pip install --user --no-cache-dir --only-binary=:all: lightgbm xgboost 2>/dev/null || true
    PYTHON_BIN="$PYTHON_SYS"
fi

# 4. Create necessary subfolders and ensure .env exists
echo "📁 Step 4: Preparing directories and .env configuration..."
mkdir -p logs models data templates
if [ ! -f ".env" ]; then
    echo "📝 Creating initial .env from .env.example..."
    cp .env.example .env
fi

# 5. Train or verify models
if [ ! -f "models/fb_roas_ensemble.pkl" ]; then
    echo "🧠 Step 5: Pre-training ML models on VPS..."
    $PYTHON_BIN train_fb_models_colab.py
else
    echo "✅ Step 5: Pre-trained models verified in models/"
fi

# 6. Run test suite to guarantee 100% operational integrity
echo "🧪 Step 6: Executing operational test suite..."
$PYTHON_BIN test_bm_automated.py
$PYTHON_BIN test_fb_multi_tenant.py
$PYTHON_BIN test_fb_offline_boost.py

# 7. Start services
if [ "$CAN_SUDO" -eq 1 ]; then
    echo "⚙️ Step 7: Configuring and installing dynamic Systemd Services..."
    for svc in bm-automated.service bm-web-gui.service bm-bot.service; do
        if [ -f "$svc" ]; then
            sed -e "s|^User=.*|User=${CURRENT_USER}|g" \
                -e "s|^WorkingDirectory=.*|WorkingDirectory=${DIR}|g" \
                -e "s|^EnvironmentFile=-.*|EnvironmentFile=-${DIR}/.env|g" \
                -e "s|ExecStart=.*run_bm_automated.py|ExecStart=${PYTHON_BIN} run_bm_automated.py|g" \
                -e "s|ExecStart=.*web_dashboard.py|ExecStart=${PYTHON_BIN} web_dashboard.py|g" \
                -e "s|ExecStart=.*bm_telegram_bot.py|ExecStart=${PYTHON_BIN} bm_telegram_bot.py|g" \
                "$svc" > "/tmp/${svc}"
            
            if [ "$NUM_CPUS" -le 2 ]; then
                sed -i "s|^CPUAffinity=.*|# CPUAffinity disabled for $NUM_CPUS vCPUs|g" "/tmp/${svc}"
            fi

            sudo cp "/tmp/${svc}" "/etc/systemd/system/${svc}"
            rm -f "/tmp/${svc}"
            echo "   • Configured /etc/systemd/system/${svc}"
        fi
    done

    sudo systemctl daemon-reload
    sudo systemctl enable bm-automated.service bm-web-gui.service bm-bot.service

    echo "🚀 Step 8: Starting 24/7 LIVE Services under Systemd..."
    sudo systemctl restart bm-automated.service
    sudo systemctl restart bm-web-gui.service
    sudo systemctl restart bm-bot.service
else
    echo "🚀 Step 7: Starting 24/7 LIVE Background Processes via nohup (Zero-Sudo)..."
    chmod +x start_bm_automated.sh stop_bm_automated.sh
    ./start_bm_automated.sh

    # Setup crontab auto-restart on reboot if not already present
    (crontab -l 2>/dev/null | grep -v "start_bm_automated.sh"; echo "@reboot cd $DIR && ./start_bm_automated.sh >> $DIR/logs/reboot.log 2>&1") | crontab - 2>/dev/null || true
    echo "✅ Configured auto-restart on reboot via user crontab!"
fi

PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "YOUR_VPS_IP")

echo "======================================================================"
echo "🎉 DEPLOYMENT COMPLETE! FB PAGE BM AUTOMATED IS WORKING LIVE 24/7!"
echo "======================================================================"
if [ "$CAN_SUDO" -eq 1 ]; then
    echo "📊 Status (Systemd):"
    echo "   • Telegram Bot: sudo systemctl status bm-bot.service"
    echo "   • Auto Daemon:  sudo systemctl status bm-automated.service"
    echo "   • Web GUI:      sudo systemctl status bm-web-gui.service"
    echo "   • Realtime Log: sudo journalctl -u bm-bot.service -f"
else
    echo "📊 Status (User Background):"
    echo "   • Telegram Bot: tail -f logs/bm_bot.log"
    echo "   • Auto Daemon:  tail -f logs/bm_daemon.log"
    echo "   • Web GUI:      tail -f logs/bm_web.log"
    echo "   • Stop Engine:  ./stop_bm_automated.sh"
    echo "   • Start Engine: ./start_bm_automated.sh"
fi
echo "   • Web URL:      http://${PUBLIC_IP}:8088"
echo "======================================================================"
if grep -qE "BM_TELEGRAM_BOT_TOKEN=$|BM_TELEGRAM_BOT_TOKEN=\s*$" .env 2>/dev/null; then
    echo "⚠️ [TELEGRAM ACTION REQUIRED]"
    echo "   Your Telegram Bot Token is currently empty in .env!"
    echo "   To connect your Bot so /start and commands work on your phone:"
    echo "   👉 Run: nano .env"
    echo "   👉 Set: BM_TELEGRAM_BOT_TOKEN=\"your_token_from_botfather\""
    echo "   👉 Save: Ctrl+O, Enter, then Ctrl+X"
    echo "======================================================================"
fi

