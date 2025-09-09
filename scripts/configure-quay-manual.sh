#!/bin/bash

# Manual configuration of Quay.io credentials (not stored in git)
echo "🔐 Manual Quay.io credentials configuration"
echo "⚠️  This approach creates secrets directly in the cluster"
echo ""

# Check if required environment variables are set
if [ -z "$QUAY_USERNAME" ] || [ -z "$QUAY_TOKEN" ]; then
    echo "❌ Please set QUAY_USERNAME and QUAY_TOKEN environment variables"
    echo ""
    echo "📋 Steps to get Quay.io robot credentials:"
    echo "1. Go to https://quay.io"
    echo "2. Navigate to Repository → ebpf-ia-kubernetes (or create it)"
    echo "3. Go to Settings → Robot Accounts"
    echo "4. Click 'Create Robot Account'"
    echo "5. Name: 'tekton-builder' or similar"
    echo "6. Permissions: Select 'Write' to this repository"
    echo "7. Copy the robot username and token"
    echo ""
    echo "Then run:"
    echo "   export QUAY_USERNAME='robot\$yourusername+tektonbuilder'"
    echo "   export QUAY_TOKEN='your-long-robot-token'"
    echo "   $0"
    exit 1
fi

# Create namespace if doesn't exist
kubectl create namespace ebpf-security --dry-run=client -o yaml | kubectl apply -f -

# Create docker config secret directly in cluster
kubectl create secret docker-registry quay-io-secret \
  --docker-server=quay.io \
  --docker-username="$QUAY_USERNAME" \
  --docker-password="$QUAY_TOKEN" \
  --docker-email="pipeline@example.com" \
  --namespace=ebpf-security \
  --dry-run=client -o yaml | kubectl apply -f -

# Annotate for Tekton
kubectl annotate secret quay-io-secret tekton.dev/docker-0=https://quay.io -n ebpf-security

# Create service account
kubectl apply -f - << EOF
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

echo "✅ Quay.io credentials configured successfully!"
echo "🔒 Credentials are stored in cluster only (not in git)"
echo ""
echo "🧪 Test the pipeline:"
echo "   kubectl apply -f gitops/pipelines/ml-detector-quay-pipeline.yaml"
echo ""
echo "📊 Monitor pipeline:"
echo "   kubectl get pipelineruns -n ebpf-security -w"