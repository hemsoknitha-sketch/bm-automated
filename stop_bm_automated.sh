#!/bin/bash
# ==============================================================================
# 🛑 FB PAGE BM AUTOMATED - PRODUCTION STOP SCRIPT
# ==============================================================================
set -e

echo "🛑 Stopping FB Page BM Automated services..."

if [ -f /tmp/bm_daemon.pid ]; then
    PID=$(cat /tmp/bm_daemon.pid)
    kill -15 "$PID" 2>/dev/null || kill -9 "$PID" 2>/dev/null || true
    rm -f /tmp/bm_daemon.pid
    echo "✅ BM Daemon stopped (PID $PID)."
fi

if [ -f /tmp/bm_web.pid ]; then
    PID=$(cat /tmp/bm_web.pid)
    kill -15 "$PID" 2>/dev/null || kill -9 "$PID" 2>/dev/null || true
    rm -f /tmp/bm_web.pid
    echo "✅ BM Web GUI stopped (PID $PID)."
fi

if [ -f /tmp/bm_bot.pid ]; then
    PID=$(cat /tmp/bm_bot.pid)
    kill -15 "$PID" 2>/dev/null || kill -9 "$PID" 2>/dev/null || true
    rm -f /tmp/bm_bot.pid
    echo "✅ BM Telegram Bot stopped (PID $PID)."
fi

if [ -f /tmp/bm_cloudflared.pid ]; then
    PID=$(cat /tmp/bm_cloudflared.pid)
    kill -15 "$PID" 2>/dev/null || kill -9 "$PID" 2>/dev/null || true
    rm -f /tmp/bm_cloudflared.pid
    echo "✅ BM Cloudflare Tunnel stopped (PID $PID)."
fi

# Fallback cleanup
pkill -f "run_bm_automated.py" 2>/dev/null || true
pkill -f "web_dashboard.py" 2>/dev/null || true
pkill -f "bm_telegram_bot.py" 2>/dev/null || true
pkill -f "cloudflared tunnel" 2>/dev/null || true

echo "✅ All BM Automated processes terminated cleanly."

