#!/bin/bash

echo "🔐 Installing Sealed Secrets for secure credential management"

# Install Sealed Secrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Wait for controller to be ready
echo "⏳ Waiting for Sealed Secrets controller..."
kubectl wait --for=condition=ready pod -l name=sealed-secrets-controller -n kube-system --timeout=120s

# Download kubeseal CLI
echo "📥 Installing kubeseal CLI..."
KUBESEAL_VERSION='0.24.0'
wget "https://github.com/bitnami-labs/sealed-secrets/releases/download/v${KUBESEAL_VERSION}/kubeseal-${KUBESEAL_VERSION}-linux-amd64.tar.gz"
tar -xzf "kubeseal-${KUBESEAL_VERSION}-linux-amd64.tar.gz"
sudo install -m 755 kubeseal /usr/local/bin/kubeseal
rm kubeseal-${KUBESEAL_VERSION}-linux-amd64.tar.gz kubeseal

echo "✅ Sealed Secrets installed successfully!"
echo ""
echo "🔑 Now you can create sealed secrets:"
echo "1. Create normal secret locally (not committed)"
echo "2. Seal it with: kubeseal -o yaml < secret.yaml > sealed-secret.yaml"
echo "3. Commit only the sealed-secret.yaml (encrypted)"