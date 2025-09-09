#!/bin/bash

# Setup Quay.io Credentials for Tekton Pipelines
echo "🔐 Setting up Quay.io Credentials for Automated Pipeline"

# Check if required environment variables are set
if [ -z "$QUAY_USERNAME" ] || [ -z "$QUAY_TOKEN" ]; then
    echo "❌ Please set QUAY_USERNAME and QUAY_TOKEN environment variables"
    echo "   export QUAY_USERNAME='your-username'"
    echo "   export QUAY_TOKEN='your-robot-token'"
    echo ""
    echo "📋 To get a Quay.io robot token:"
    echo "1. Go to https://quay.io"
    echo "2. Navigate to your repository: ebpf-ia-kubernetes"
    echo "3. Go to Settings > Robot Accounts"
    echo "4. Create a robot account with 'write' permissions"
    echo "5. Copy the token and username"
    exit 1
fi

# Create base64 encoded auth string
AUTH_STRING=$(echo -n "$QUAY_USERNAME:$QUAY_TOKEN" | base64 -w 0)

# Create the docker config JSON
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

# Update the secret file
SECRET_FILE="gitops/secrets/quay-io-secret.yaml"
cat > "$SECRET_FILE" << EOF
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
$(echo "$DOCKER_CONFIG" | sed 's/^/    /')
---
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

echo "✅ Quay.io credentials configured in $SECRET_FILE"
echo "🚀 Next steps:"
echo "   1. git add $SECRET_FILE"
echo "   2. git commit -m 'Configure Quay.io credentials for pipeline'"
echo "   3. git push origin main"
echo "   4. ArgoCD will automatically deploy the credentials"
echo "   5. Run pipeline: kubectl apply -f gitops/pipelines/ml-detector-quay-pipeline.yaml"