#!/bin/bash
# ==============================================================================
# 🚀 FB PAGE BM AUTOMATED - PRODUCTION START SCRIPT (LINUX GCP VPS)
# ==============================================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "======================================================================"
echo "🚀 [BM AUTOMATED] STARTING DAEMON & WEB GUI ON LINUX VPS..."
echo "======================================================================"

# Verify Python
if [ -f "$DIR/venv/bin/python3" ]; then
    PYTHON_BIN="$DIR/venv/bin/python3"
else
    PYTHON_BIN=$(which python3 || echo "/usr/bin/python3")
fi

# Ensure unbuffered python output so logs appear instantly
export PYTHONUNBUFFERED=1

# Ensure required directories exist
mkdir -p logs models data

# Start Daemon in background with rotating log
nohup $PYTHON_BIN -u run_bm_automated.py --daemon --interval 300 >> logs/bm_daemon.log 2>&1 &
DAEMON_PID=$!
echo "$DAEMON_PID" > /tmp/bm_daemon.pid
echo "✅ [DAEMON] Started with PID: $DAEMON_PID (Logging to logs/bm_daemon.log)"

# Start Web GUI in background on Port 8088
nohup $PYTHON_BIN -u web_dashboard.py >> logs/bm_web.log 2>&1 &
WEB_PID=$!
echo "$WEB_PID" > /tmp/bm_web.pid
echo "✅ [WEB GUI] Started on http://0.0.0.0:8088 with PID: $WEB_PID (Logging to logs/bm_web.log)"

# Start Telegram Bot Controller in background
nohup $PYTHON_BIN -u bm_telegram_bot.py >> logs/bm_bot.log 2>&1 &
BOT_PID=$!
echo "$BOT_PID" > /tmp/bm_bot.pid
echo "✅ [TELEGRAM BOT] Started with PID: $BOT_PID (Logging to logs/bm_bot.log)"

echo "======================================================================"
echo "🎉 FB PAGE BM AUTOMATED is running LIVE 24/7!"
echo "   • Status:  tail -f logs/bm_daemon.log"
echo "   • Web GUI: http://<VPS_IP>:8088"
echo "======================================================================"

