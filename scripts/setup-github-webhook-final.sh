#!/bin/bash

# Setup GitHub Webhook for automated Tekton pipeline execution
echo "🔗 Setting up GitHub Webhook for Tekton Pipeline Automation"
echo "=========================================================="

# Get node IP and webhook URL
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
WEBHOOK_PORT=30082
WEBHOOK_URL="http://${NODE_IP}:${WEBHOOK_PORT}"

echo "📍 Internal Webhook Configuration:"
echo "   Internal URL: ${WEBHOOK_URL}"
echo "   Secret: [sealed-secret] (see sealed-secrets/README.md)"
echo "   Content-Type: application/json"
echo "   Events: Push events only"
echo ""
echo "⚠️  PROBLEMA: GitHub no puede acceder a IP interna (${NODE_IP})"
echo ""
echo "🌐 OPCIONES PARA ACCESO PÚBLICO:"
echo "================================"
echo "1. 🔧 WILDCARD DOMAIN (Recomendado para producción):"
echo "   - URL: https://webhook.apps.k8s.labjp.xyz"
echo "   - Requiere: DNS wildcard configurado"
echo ""
echo "2. 🚇 NGROK TUNNEL (Para desarrollo/testing):"
echo "   - Ejecutar: ./scripts/setup-webhook-ngrok.sh"
echo "   - Crea URL pública temporal"
echo ""
echo "3. 🏠 PORT FORWARD + NGROK (Alternativa):"
echo "   - kubectl port-forward svc/el-github-webhook-listener -n ebpf-security 8080:8080"
echo "   - ngrok http 8080"
echo ""

echo "🔧 GitHub Repository Configuration Steps:"
echo "----------------------------------------"
echo "1. Go to: https://github.com/jeanlopezxyz/ebpf-ia-kubernetes"
echo "2. Navigate to: Settings > Webhooks"
echo "3. Click: Add webhook"
echo "4. Configure:"
echo "   - Payload URL: ${WEBHOOK_URL}"
echo "   - Content type: application/json"
echo "   - Secret: [sealed-secret] (see sealed-secrets/README.md)"
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