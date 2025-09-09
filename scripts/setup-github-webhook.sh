#!/bin/bash

# Setup GitHub Webhook for Tekton Pipeline Automation
echo "🔗 Setting up GitHub Webhook for Tekton Pipeline Automation"

# Get NodePort for webhook listener
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
WEBHOOK_PORT=30080
WEBHOOK_URL="http://${NODE_IP}:${WEBHOOK_PORT}"

echo "📍 Webhook URL: ${WEBHOOK_URL}"
echo "🔐 Secret Token: webhook-secret-token-2024"

echo ""
echo "📋 GitHub Webhook Configuration Steps:"
echo "1. Go to your GitHub repository: https://github.com/jeanlopezxyz/ebpf-ia-kubernetes"
echo "2. Navigate to Settings > Webhooks > Add webhook"
echo "3. Set Payload URL: ${WEBHOOK_URL}"
echo "4. Set Content type: application/json"
echo "5. Set Secret: webhook-secret-token-2024"
echo "6. Select events: Just the push event"
echo "7. Ensure Active is checked"
echo "8. Click Add webhook"

echo ""
echo "🚀 Test the webhook:"
echo "   git push origin main"
echo "   kubectl get pipelineruns -n ebpf-security"

echo ""
echo "🔍 Monitor webhook events:"
echo "   kubectl logs -f -l eventlistener=github-webhook-listener -n ebpf-security"
echo "   kubectl get events -n ebpf-security --sort-by='.lastTimestamp'"

echo ""
echo "✅ Webhook setup complete! Push to main branch will automatically trigger ML detector pipeline."