#!/bin/bash
# ==============================================================================
# 🌐 CLOUDFLARE TUNNEL (CLOUDFLARED) - 1-CLICK FREE HTTPS & ZERO-FIREWALL SETUP
# ==============================================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "======================================================================"
echo "🌐 [CLOUDFLARE TUNNEL] SETTING UP FREE ZERO-CONFIG HTTPS WEB ACCESS..."
echo "======================================================================"

# 1. Download cloudflared if not present
if ! command -v cloudflared &> /dev/null; then
    if [ ! -f "$DIR/cloudflared" ]; then
        echo "📥 Downloading official cloudflared binary (Linux amd64)..."
        curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o "$DIR/cloudflared"
        chmod +x "$DIR/cloudflared"
        # Try to install to /usr/local/bin if sudo/root available
        if [ "$EUID" -eq 0 ] || sudo -n true 2>/dev/null; then
            sudo cp "$DIR/cloudflared" /usr/local/bin/cloudflared 2>/dev/null || true
        fi
    fi
    CLOUDFLARED_BIN="$DIR/cloudflared"
else
    CLOUDFLARED_BIN=$(which cloudflared)
fi

echo "✅ Cloudflared is ready: $($CLOUDFLARED_BIN --version | head -n 1)"

# 2. Stop any existing cloudflared instance
if [ -f /tmp/bm_cloudflared.pid ]; then
    OLD_PID=$(cat /tmp/bm_cloudflared.pid)
    kill -15 "$OLD_PID" 2>/dev/null || true
    rm -f /tmp/bm_cloudflared.pid
fi
pkill -f "cloudflared tunnel" 2>/dev/null || true

# 3. Start Cloudflare Quick Tunnel in background
mkdir -p logs
echo "🚀 Starting Cloudflare Quick Tunnel for http://localhost:8088..."
nohup $CLOUDFLARED_BIN tunnel --url http://localhost:8088 > logs/cloudflare_tunnel.log 2>&1 &
TUNNEL_PID=$!
echo "$TUNNEL_PID" > /tmp/bm_cloudflared.pid

# 4. Wait for URL to appear (up to 15s)
echo "⏳ Waiting for Cloudflare HTTPS Public URL..."
TUNNEL_URL=""
for i in {1..15}; do
    sleep 1
    if grep -q "trycloudflare.com" logs/cloudflare_tunnel.log 2>/dev/null; then
        TUNNEL_URL=$(grep -o 'https://[a-zA-Z0-9.-]*\.trycloudflare\.com' logs/cloudflare_tunnel.log | head -n 1)
        if [ -n "$TUNNEL_URL" ]; then
            break
        fi
    fi
done

echo "======================================================================"
if [ -n "$TUNNEL_URL" ]; then
    echo "🎉 CLOUDFLARE HTTPS TUNNEL IS LIVE!"
    echo "🔗 URL: $TUNNEL_URL"
    echo "🛡️ SSL: 100% Free HTTPS Green Lock Active"
    echo "⚡ Speed: Anycast Cloudflare Edge (Global & Cambodia CDN)"
    echo "🔒 Firewall: Zero GCP Firewall Rules needed (Zero Open Ports!)"
    echo "======================================================================"
    echo "💡 លោកបងអាចបើក Web Dashboard តាមរយៈ Link ខាងលើបានភ្លាមៗ!"
else
    echo "⚠️ Cloudflare tunnel is starting in background. Check: tail -f logs/cloudflare_tunnel.log"
    echo "======================================================================"
fi
