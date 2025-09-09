#!/bin/bash

# Setup GitHub Webhook using ngrok for public access
echo "🌐 Setting up GitHub Webhook with ngrok tunnel"
echo "=============================================="

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "📥 Installing ngrok..."
    curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
    sudo apt update && sudo apt install ngrok -y
fi

# Get local NodePort
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
WEBHOOK_PORT=30082
LOCAL_URL="http://${NODE_IP}:${WEBHOOK_PORT}"

echo "🔗 Local webhook endpoint: ${LOCAL_URL}"
echo ""
echo "🚀 Starting ngrok tunnel..."
echo "   This will create a public URL for GitHub webhook"
echo ""

# Start ngrok tunnel (background)
ngrok http $WEBHOOK_PORT --log=stdout > /tmp/ngrok.log &
NGROK_PID=$!

echo "⏳ Waiting for ngrok tunnel to establish..."
sleep 5

# Get public URL from ngrok
PUBLIC_URL=$(curl -s localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url' 2>/dev/null || echo "")

if [ -z "$PUBLIC_URL" ]; then
    echo "❌ Failed to get ngrok URL. Check if ngrok is running:"
    echo "   curl localhost:4040/api/tunnels"
    kill $NGROK_PID 2>/dev/null
    exit 1
fi

echo "✅ Ngrok tunnel established!"
echo ""
echo "📋 GITHUB WEBHOOK CONFIGURATION:"
echo "================================="
echo "URL: ${PUBLIC_URL}"
echo "Content-Type: application/json"
echo "Secret: [sealed-secret] (see sealed-secrets/README.md)"
echo "Events: Just the push event"
echo ""
echo "🔧 Steps to configure in GitHub:"
echo "1. Go to: https://github.com/jeanlopezxyz/ebpf-ia-kubernetes/settings/hooks"
echo "2. Add webhook with URL: ${PUBLIC_URL}"
echo "3. Set secret: [sealed-secret] (see sealed-secrets/README.md)"
echo ""
echo "🧪 Test webhook:"
echo "   Make a change in applications/ and push to main"
echo "   Monitor: kubectl get pipelineruns -n ebpf-security -w"
echo ""
echo "⚠️  Keep this terminal open to maintain the tunnel"
echo "   Press Ctrl+C to stop ngrok tunnel"
echo ""

# Keep ngrok running
wait $NGROK_PID