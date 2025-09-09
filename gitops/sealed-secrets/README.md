# Sealed Secrets - Secure Credential Management

This directory contains encrypted secrets that are safe to commit to Git.

## 🔐 Available Sealed Secrets

### 1. Grafana Admin Credentials
- **File**: `grafana-admin-secret-sealed.yaml`
- **Namespace**: `grafana`
- **Keys**: `admin-user`, `admin-password`
- **Usage**: Grafana admin login

### 2. ArgoCD Admin Credentials  
- **File**: `argocd-admin-secret-sealed.yaml`
- **Namespace**: `argocd`
- **Keys**: `password`, `mtime`
- **Usage**: ArgoCD admin login

### 3. Quay.io Registry Credentials
- **File**: `quay-io-secret-sealed.yaml`
- **Namespace**: `ebpf-security`
- **Type**: `dockerconfigjson`
- **Usage**: Tekton pipeline registry authentication

### 4. Tekton Service Account
- **File**: `tekton-serviceaccount.yaml`
- **Namespace**: `ebpf-security`
- **Usage**: Links Quay.io credentials to Tekton pipelines

### 5. GitHub Webhook Secret
- **File**: `github-webhook-secret-sealed.yaml`
- **Namespace**: `ebpf-security`
- **Keys**: `secretToken`
- **Usage**: GitHub webhook validation

## 🚀 Generated Passwords

**IMPORTANT**: Save these credentials securely - they are only shown once:

- **Grafana Admin**: `MIVl6ww1DkKZidZyuHHXS5c4N`
- **ArgoCD Admin**: `oSsMYDYPSzcXXexpW2GdSrM2g`
- **GitHub Webhook**: `2N1ydZkoZ1iuZPHn5mnI0A8bK`

## 🔄 Updating Secrets

To update any sealed secret:

1. **Modify the source secret** (locally, not in Git)
2. **Seal it again**:
   ```bash
   kubectl create secret generic my-secret --from-literal=key=value --dry-run=client -o yaml | kubeseal -o yaml > my-secret-sealed.yaml
   ```
3. **Commit the sealed secret** - it's encrypted and safe

## 🛡️ Security Notes

- ✅ **Sealed secrets are encrypted** with the cluster's public key
- ✅ **Only the cluster** can decrypt them
- ✅ **Safe to store in Git** - no plaintext credentials
- ✅ **Automatic rotation** when sealed secrets controller key rotates

## 🎯 Real Quay.io Setup

To replace the example Quay.io credentials:

1. **Get Quay.io robot credentials**:
   - Go to https://quay.io
   - Repository Settings → Robot Accounts
   - Create robot with `Write` permissions

2. **Create real sealed secret**:
   ```bash
   export QUAY_USERNAME="robot$yourusername+tektonbuilder"  
   export QUAY_TOKEN="your-real-robot-token"
   
   kubectl create secret docker-registry quay-io-secret \
     --docker-server=quay.io \
     --docker-username="$QUAY_USERNAME" \
     --docker-password="$QUAY_TOKEN" \
     --docker-email="pipeline@example.com" \
     --namespace=ebpf-security \
     --dry-run=client -o yaml | kubeseal -o yaml > quay-io-secret-sealed.yaml
   ```

3. **Commit and push** - ArgoCD will apply automatically