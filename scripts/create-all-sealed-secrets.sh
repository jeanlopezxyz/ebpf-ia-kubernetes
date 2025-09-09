#!/bin/bash

# Create all Sealed Secrets for the eBPF AI platform
echo "🔐 Creating All Sealed Secrets for eBPF AI Platform"
echo "=================================================="

# Check if Sealed Secrets controller is ready
echo "⏳ Checking if Sealed Secrets controller is ready..."
if ! kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=sealed-secrets -n kube-system --timeout=60s; then
    echo "❌ Sealed Secrets controller not ready. Please wait for ArgoCD to deploy it."
    echo "   kubectl get applications sealed-secrets -n argocd"
    exit 1
fi

# Install kubeseal CLI if needed
if ! command -v kubeseal &> /dev/null; then
    echo "📥 Installing kubeseal CLI..."
    KUBESEAL_VERSION='0.24.0'
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        ARCH="amd64"
    elif [ "$ARCH" = "aarch64" ]; then
        ARCH="arm64"
    fi
    
    curl -L "https://github.com/bitnami-labs/sealed-secrets/releases/download/v${KUBESEAL_VERSION}/kubeseal-${KUBESEAL_VERSION}-linux-${ARCH}.tar.gz" | tar -xz
    sudo install -m 755 kubeseal /usr/local/bin/kubeseal
    rm kubeseal
    echo "✅ kubeseal CLI installed"
fi

# Function to create sealed secret
create_sealed_secret() {
    local secret_name=$1
    local namespace=$2
    local temp_file="/tmp/${secret_name}-temp.yaml"
    local sealed_file="gitops/sealed-secrets/${secret_name}-sealed.yaml"
    
    # Create directory if it doesn't exist
    mkdir -p "gitops/sealed-secrets"
    
    # Create temporary secret
    shift 2  # Remove first two arguments
    kubectl create secret generic "$secret_name" \
        --namespace="$namespace" \
        --dry-run=client \
        -o yaml \
        "$@" > "$temp_file"
    
    # Create sealed secret
    kubeseal -f "$temp_file" -w "$sealed_file"
    
    # Clean up
    rm "$temp_file"
    
    echo "✅ Created sealed secret: $sealed_file"
}

# 1. GRAFANA ADMIN PASSWORD
echo ""
echo "🎯 1. Creating Grafana admin password sealed secret..."
GRAFANA_ADMIN_PASSWORD="${GRAFANA_ADMIN_PASSWORD:-$(openssl rand -base64 32 | tr -d '=+/' | cut -c1-25)}"
echo "   Generated password: $GRAFANA_ADMIN_PASSWORD"

create_sealed_secret "grafana-admin-secret" "grafana" \
    --from-literal=admin-password="$GRAFANA_ADMIN_PASSWORD"

# 2. ARGOCD ADMIN PASSWORD  
echo ""
echo "🎯 2. Creating ArgoCD admin password sealed secret..."
ARGOCD_ADMIN_PASSWORD="${ARGOCD_ADMIN_PASSWORD:-$(openssl rand -base64 32 | tr -d '=+/' | cut -c1-25)}"
ARGOCD_PASSWORD_HASH=$(htpasswd -bnBC 10 "" "$ARGOCD_ADMIN_PASSWORD" | tr -d ':\n')
echo "   Generated password: $ARGOCD_ADMIN_PASSWORD"

create_sealed_secret "argocd-admin-secret" "argocd" \
    --from-literal=password="$ARGOCD_PASSWORD_HASH" \
    --from-literal=mtime="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

# 3. QUAY.IO CREDENTIALS (only if provided)
echo ""
echo "🎯 3. Creating Quay.io credentials sealed secret..."
if [ -n "$QUAY_USERNAME" ] && [ -n "$QUAY_TOKEN" ]; then
    AUTH_STRING=$(echo -n "$QUAY_USERNAME:$QUAY_TOKEN" | base64 -w 0)
    
    DOCKER_CONFIG=$(cat <<EOF
{
  "auths": {
    "quay.io": {
      "username": "$QUAY_USERNAME",
      "password": "$QUAY_TOKEN", 
      "email": "pipeline@example.com",
      "auth": "$AUTH_STRING"
    }
  }
}
EOF
)
    
    # Create dockerconfigjson secret
    kubectl create secret docker-registry quay-io-secret \
        --docker-server=quay.io \
        --docker-username="$QUAY_USERNAME" \
        --docker-password="$QUAY_TOKEN" \
        --docker-email="pipeline@example.com" \
        --namespace=ebpf-security \
        --dry-run=client -o yaml > /tmp/quay-secret-temp.yaml
    
    # Add Tekton annotation
    kubectl annotate secret quay-io-secret tekton.dev/docker-0=https://quay.io \
        --dry-run=client -o yaml --local=true -f /tmp/quay-secret-temp.yaml > /tmp/quay-annotated-temp.yaml
    
    kubeseal -f /tmp/quay-annotated-temp.yaml -w gitops/sealed-secrets/quay-io-secret-sealed.yaml
    
    rm /tmp/quay-secret-temp.yaml /tmp/quay-annotated-temp.yaml
    
    # Create ServiceAccount for Tekton
    cat > gitops/sealed-secrets/tekton-serviceaccount.yaml << EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: tekton-builder-sa
  namespace: ebpf-security
secrets:
  - name: quay-io-secret
imagePullSecrets:
  - name: quay-io-secret
EOF
    
    echo "✅ Created sealed Quay.io credentials and ServiceAccount"
else
    echo "⚠️  Skipping Quay.io credentials (QUAY_USERNAME and QUAY_TOKEN not set)"
    echo "   Set them and re-run to create Quay.io sealed secret:"
    echo "   export QUAY_USERNAME='robot\$yourusername+tektonbuilder'"
    echo "   export QUAY_TOKEN='your-robot-token'"
fi

# Summary
echo ""
echo "🎉 SEALED SECRETS CREATION COMPLETED!"
echo "====================================="
echo ""
echo "📁 Created files:"
ls -la gitops/sealed-secrets/
echo ""
echo "💾 Generated passwords (SAVE THESE SECURELY):"
echo "   Grafana admin: $GRAFANA_ADMIN_PASSWORD"
echo "   ArgoCD admin:  $ARGOCD_ADMIN_PASSWORD"
echo ""
echo "🚀 Next steps:"
echo "   1. git add gitops/sealed-secrets/"
echo "   2. git commit -m 'Add sealed secrets for all services'"
echo "   3. git push origin main"
echo "   4. Update Helm charts to use sealed secrets"