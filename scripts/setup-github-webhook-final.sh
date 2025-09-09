#!/bin/bash

# Setup GitHub Webhook for automated Tekton pipeline execution
echo "🔗 Setting up GitHub Webhook for Tekton Pipeline Automation"
echo "=========================================================="

# Get node IP and webhook URL
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
WEBHOOK_PORT=30082
WEBHOOK_URL="http://${NODE_IP}:${WEBHOOK_PORT}"

echo "📍 Webhook Configuration:"
echo "   URL: ${WEBHOOK_URL}"
echo "   Secret: webhook-secret-token-2024"
echo "   Content-Type: application/json"
echo "   Events: Push events only"
echo ""

echo "🔧 GitHub Repository Configuration Steps:"
echo "----------------------------------------"
echo "1. Go to: https://github.com/jeanlopezxyz/ebpf-ia-kubernetes"
echo "2. Navigate to: Settings > Webhooks"
echo "3. Click: Add webhook"
echo "4. Configure:"
echo "   - Payload URL: ${WEBHOOK_URL}"
echo "   - Content type: application/json"
echo "   - Secret: webhook-secret-token-2024"
echo "   - Which events: Just the push event"
echo "   - Active: ✓ (checked)"
echo "5. Click: Add webhook"
echo ""

echo "📊 Verify EventListener is running:"
kubectl get pods -n ebpf-security -l eventlistener=github-webhook-listener

echo ""
echo "🧪 Test webhook manually:"
echo "curl -X POST ${WEBHOOK_URL} \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'X-GitHub-Event: push' \\"
echo "  -H 'X-Hub-Signature-256: sha256=...' \\"
echo "  -d '{\"ref\":\"refs/heads/main\",\"head_commit\":{\"modified\":[\"applications/ml-detector/test\"]}}')"
echo ""

echo "🔍 Monitor pipeline execution:"
echo "   kubectl get pipelineruns -n ebpf-security -w"
echo "   kubectl get eventlisteners -n ebpf-security"
echo "   kubectl logs -f -l eventlistener=github-webhook-listener -n ebpf-security"
echo ""

echo "✅ Once configured, any push to main that modifies applications/ will:"
echo "   1. Trigger GitHub webhook"
echo "   2. Execute Tekton pipeline"
echo "   3. Build image with latest code"
echo "   4. Push to quay.io/jealopez/ml-detector:latest"
echo "   5. ArgoCD redeploys automatically"