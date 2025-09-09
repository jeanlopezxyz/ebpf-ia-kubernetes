#!/bin/bash

# Create Sealed Secret for Quay.io credentials
echo "🔐 Creating Sealed Secret for Quay.io credentials"

# Check if required environment variables are set
if [ -z "$QUAY_USERNAME" ] || [ -z "$QUAY_TOKEN" ]; then
    echo "❌ Please set QUAY_USERNAME and QUAY_TOKEN environment variables"
    echo "   export QUAY_USERNAME='robot\$yourusername+yourrobot'"
    echo "   export QUAY_TOKEN='your-robot-token'"
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
SEALED_SECRET_FILE="gitops/secrets/quay-io-sealed-secret.yaml"
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