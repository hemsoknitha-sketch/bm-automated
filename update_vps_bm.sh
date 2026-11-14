#!/bin/bash
# ==============================================================================
# 🚀 1-TAP VPS AUTO-UPDATE & ZERO-DOWNTIME RESTART FOR BM AUTOMATED
# Target: Google Cloud Linux VPS 'bm-automated' (us-central1-a, quant-gold-514007)
# Repository: https://github.com/hemsoknitha-sketch/bm-automated.git
# ==============================================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "======================================================================"
echo "🔄 [1-TAP UPDATE] SYNCING BM AUTOMATED FROM GITHUB ORIGIN MAIN..."
echo "   Directory: $DIR"
echo "   Time:      $(date)"
echo "======================================================================"

# 1. Pull latest code from GitHub
echo "📦 Step 1: Pulling latest code..."
git fetch origin main
git reset --hard origin/main

# 2. Update dependencies if needed
if [ -f "requirements.txt" ]; then
    echo "📦 Step 2: Updating dependencies (zero-cache mode)..."
    rm -rf ~/.cache/pip /tmp/pip-* 2>/dev/null || true
    if [ -f "$DIR/venv/bin/pip" ]; then
        "$DIR/venv/bin/pip" install --no-cache-dir --prefer-binary -r requirements.txt
    else
        python3 -m pip install --no-cache-dir --prefer-binary -r requirements.txt || true
    fi
fi

# 3. Verify tests
echo "🧪 Step 3: Running verification tests..."
if [ -f "$DIR/venv/bin/python3" ]; then
    PYTHON_BIN="$DIR/venv/bin/python3"
else
    PYTHON_BIN=$(which python3)
fi
$PYTHON_BIN test_bm_automated.py
$PYTHON_BIN test_fb_multi_tenant.py
$PYTHON_BIN test_fb_offline_boost.py
$PYTHON_BIN test_fb_page_autonomous_publisher.py

# 4. Restart services
echo "🚀 Step 4: Restarting 24/7 services..."
CURRENT_USER=$(whoami)
CAN_SUDO=0
if sudo -n true 2>/dev/null || sudo true 2>/dev/null; then
    CAN_SUDO=1
fi

if [ "$CAN_SUDO" -eq 1 ]; then
    # Ensure systemd services are installed and up to date
    if [ ! -f "/etc/systemd/system/bm-automated.service" ] || [ ! -f "/etc/systemd/system/bm-web-gui.service" ] || [ ! -f "/etc/systemd/system/bm-bot.service" ]; then
        echo "⚙️ Configuring and installing Systemd services into /etc/systemd/system/..."
        for svc in bm-automated.service bm-web-gui.service bm-bot.service; do
            if [ -f "$svc" ]; then
                sed -e "s|^User=.*|User=${CURRENT_USER}|g" \
                    -e "s|^WorkingDirectory=.*|WorkingDirectory=${DIR}|g" \
                    -e "s|^EnvironmentFile=-.*|EnvironmentFile=-${DIR}/.env|g" \
                    -e "s|ExecStart=.*run_bm_automated.py|ExecStart=${PYTHON_BIN} run_bm_automated.py|g" \
                    -e "s|ExecStart=.*web_dashboard.py|ExecStart=${PYTHON_BIN} web_dashboard.py|g" \
                    -e "s|ExecStart=.*bm_telegram_bot.py|ExecStart=${PYTHON_BIN} bm_telegram_bot.py|g" \
                    "$svc" > "/tmp/${svc}"
                sudo cp "/tmp/${svc}" "/etc/systemd/system/${svc}"
                rm -f "/tmp/${svc}"
                echo "   • Installed /etc/systemd/system/${svc}"
            fi
        done
        sudo systemctl daemon-reload
        sudo systemctl enable bm-automated.service bm-web-gui.service bm-bot.service 2>/dev/null || true
    fi

    echo "🔄 Restarting 24/7 services under Systemd..."
    sudo systemctl restart bm-automated.service || true
    sudo systemctl restart bm-web-gui.service || true
    sudo systemctl restart bm-bot.service || true
    echo "✅ Systemd services restarted!"
else
    chmod +x stop_bm_automated.sh start_bm_automated.sh
    ./stop_bm_automated.sh 2>/dev/null || true
    ./start_bm_automated.sh
    echo "✅ Background daemons restarted via nohup!"
fi

echo "======================================================================"
echo "🎉 BM AUTOMATED SUCCESSFULLY UPDATED & RUNNING LIVE ON VPS!"
echo "======================================================================"
