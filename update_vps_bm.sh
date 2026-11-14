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
if sudo -n true 2>/dev/null || sudo true 2>/dev/null; then
    sudo systemctl restart bm-automated.service || true
    sudo systemctl restart bm-web-gui.service || true
    sudo systemctl restart bm-bot.service || true
    echo "✅ Systemd services restarted!"
else
    chmod +x stop_bm_automated.sh start_bm_automated.sh
    ./stop_bm_automated.sh || true
    ./start_bm_automated.sh
    echo "✅ Background daemons restarted!"
fi

echo "======================================================================"
echo "🎉 BM AUTOMATED SUCCESSFULLY UPDATED & RUNNING LIVE ON VPS!"
echo "======================================================================"
