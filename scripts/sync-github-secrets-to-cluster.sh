#!/bin/bash

# Sync GitHub Secrets to Kubernetes cluster for Tekton usage
echo "🔄 Syncing GitHub Repository Secrets to Kubernetes cluster"

# This script would be run manually or via GitHub Actions to sync secrets
# It reads from GitHub API and creates Kubernetes secrets for Tekton

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GITHUB_TOKEN environment variable required"
    echo "   Create a Personal Access Token with 'repo' permissions"
    exit 1
fi

REPO="jeanlopezxyz/ebpf-ia-kubernetes"
NAMESPACE="ebpf-security"

# Function to get GitHub secret (requires GitHub CLI or API call)
get_github_secret() {
    local secret_name=$1
    # This would use GitHub CLI: gh secret list --repo $REPO
    # For now, prompt user to set environment variables
    echo "Please set these environment variables from your GitHub Secrets:"
    echo "export QUAY_USERNAME_FROM_GITHUB='value-from-github-secret'"
    echo "export QUAY_TOKEN_FROM_GITHUB='value-from-github-secret'"
}

echo "📋 Manual sync process:"
echo "1. Go to GitHub → Repository → Settings → Secrets and variables → Actions"
echo "2. Add secrets: QUAY_USERNAME and QUAY_TOKEN"
echo "3. Run this script with those values as environment variables"
echo ""

if [ -z "$QUAY_USERNAME_FROM_GITHUB" ] || [ -z "$QUAY_TOKEN_FROM_GITHUB" ]; then
    echo "⚠️  Set environment variables from GitHub Secrets:"
    echo "   export QUAY_USERNAME_FROM_GITHUB='robot\$user+robot'"
    echo "   export QUAY_TOKEN_FROM_GITHUB='github-secret-token-value'"
    exit 1
fi

# Create Kubernetes secret from GitHub secret values
kubectl create secret docker-registry quay-io-secret \
  --docker-server=quay.io \
  --docker-username="$QUAY_USERNAME_FROM_GITHUB" \
  --docker-password="$QUAY_TOKEN_FROM_GITHUB" \
  --docker-email="pipeline@example.com" \
  --namespace=$NAMESPACE \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl annotate secret quay-io-secret tekton.dev/docker-0=https://quay.io -n $NAMESPACE --overwrite

# Create ServiceAccount for Tekton
kubectl apply -f - << EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: tekton-builder-sa
  namespace: $NAMESPACE
secrets:
  - name: quay-io-secret
imagePullSecrets:
  - name: quay-io-secret
EOF

echo "✅ GitHub Secrets synced to Kubernetes cluster!"
echo "🚀 Tekton pipelines can now use these credentials"