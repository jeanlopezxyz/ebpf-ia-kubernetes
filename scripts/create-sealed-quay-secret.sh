#!/bin/bash

# Create Sealed Secret for Quay.io credentials
echo "🔐 Creating Sealed Secret for Quay.io credentials"

# Check if sealed-secrets controller is running
echo "⏳ Checking if Sealed Secrets controller is ready..."
if ! kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=sealed-secrets -n kube-system --timeout=60s; then
    echo "❌ Sealed Secrets controller not ready. Please ensure it's installed via ArgoCD:"
    echo "   kubectl get applications sealed-secrets -n argocd"
    exit 1
fi

# Check if kubeseal CLI is available
if ! command -v kubeseal &> /dev/null; then
    echo "📥 Installing kubeseal CLI..."
    KUBESEAL_VERSION='0.24.0'
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        ARCH="amd64"
    elif [ "$ARCH" = "aarch64" ]; then
        ARCH="arm64"
    fi
    
    wget "https://github.com/bitnami-labs/sealed-secrets/releases/download/v${KUBESEAL_VERSION}/kubeseal-${KUBESEAL_VERSION}-linux-${ARCH}.tar.gz"
    tar -xzf "kubeseal-${KUBESEAL_VERSION}-linux-${ARCH}.tar.gz"
    sudo install -m 755 kubeseal /usr/local/bin/kubeseal
    rm "kubeseal-${KUBESEAL_VERSION}-linux-${ARCH}.tar.gz" kubeseal
    echo "✅ kubeseal CLI installed"
fi

# Check if required environment variables are set
if [ -z "$QUAY_USERNAME" ] || [ -z "$QUAY_TOKEN" ]; then
    echo "❌ Please set QUAY_USERNAME and QUAY_TOKEN environment variables"
    echo ""
    echo "📋 Steps to get Quay.io robot credentials:"
    echo "1. Go to https://quay.io"
    echo "2. Navigate to Repository → ebpf-ia-kubernetes (or create it)"
    echo "3. Go to Settings → Robot Accounts"
    echo "4. Click 'Create Robot Account'"
    echo "5. Name: 'tekton-builder' with Write permissions"
    echo "6. Copy the credentials:"
    echo ""
    echo "   export QUAY_USERNAME='robot\$yourusername+tektonbuilder'"
    echo "   export QUAY_TOKEN='your-long-robot-token'"
    echo "   $0"
    exit 1
fi

# Create temporary secret file (not committed to git)
TEMP_SECRET="/tmp/quay-secret-temp.yaml"
AUTH_STRING=$(echo -n "$QUAY_USERNAME:$QUAY_TOKEN" | base64 -w 0)

cat > "$TEMP_SECRET" << EOF
apiVersion: v1
kind: Secret
metadata:
  name: quay-io-secret
  namespace: ebpf-security
  annotations:
    tekton.dev/docker-0: https://quay.io
type: kubernetes.io/dockerconfigjson
stringData:
  .dockerconfigjson: |
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

# Create sealed secret
SEALED_SECRET_FILE="gitops/sealed-secrets/quay-io-sealed-secret.yaml"
kubeseal -f "$TEMP_SECRET" -w "$SEALED_SECRET_FILE"

# Clean up temp file
rm "$TEMP_SECRET"

echo "✅ Sealed secret created at: $SEALED_SECRET_FILE"
echo "🔒 This file is encrypted and safe to commit to git"
echo ""
echo "🚀 Next steps:"
echo "   git add $SEALED_SECRET_FILE"
echo "   git commit -m 'Add sealed Quay.io credentials'"
echo "   git push origin main"