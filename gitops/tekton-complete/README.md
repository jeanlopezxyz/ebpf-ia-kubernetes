# Tekton Complete Automation

**UNIFIED** Tekton Triggers + Webhook automation in a single ArgoCD application.

## 🎯 What This Contains

**EVERYTHING Tekton automation in ONE place:**

### 1. Tekton Triggers Installation
- **PreSync Job**: Installs official Tekton Triggers via kubectl
- **Components**: Controller, Webhook, Core Interceptors
- **ClusterInterceptors**: github, cel, gitlab, bitbucket, slack

### 2. Webhook Automation
- **EventListener**: Receives GitHub webhooks
- **TriggerBinding**: Extracts GitHub payload data
- **TriggerTemplate**: Creates PipelineRun automatically
- **RBAC**: ServiceAccount with proper permissions

### 3. Network Exposure
- **Ingress**: Exposes webhook via https://webhook.apps.k8s.labjp.xyz
- **NodePort Service**: Port 30082 for webhook endpoint
- **TLS**: Automatic certificate management

## 🔐 Security

- **GitHub Webhook Secret**: Managed via Sealed Secret
- **Quay.io Credentials**: Integrated via tekton-builder-sa
- **RBAC**: Least privilege permissions

## 🚀 Automation Flow

```
GitHub Push → https://webhook.apps.k8s.labjp.xyz → EventListener → TriggerTemplate → PipelineRun → Quay.io → ArgoCD
```

## 📋 Configuration

### GitHub Webhook Setup
- **URL**: `https://webhook.apps.k8s.labjp.xyz`
- **Secret**: Check `sealed-secrets/README.md` for current value
- **Events**: Push to main branch only

### Pipeline Triggers
- **Branch**: `main`
- **Path Filter**: Changes in `applications/` directory
- **Target**: `quay.io/jealopez/ml-detector:latest`

## 🔄 Managed by ArgoCD

- **Application**: `tekton-automation-complete`
- **Sync Wave**: `0` (with base platform)
- **Auto Sync**: Enabled with prune and self-heal
- **Dependencies**: Tekton Pipelines, Sealed Secrets

## ⚠️ Cluster Recreation

This application ensures complete automation is restored on cluster recreation:

1. **PreSync Job** installs Tekton Triggers base
2. **Main Sync** deploys webhook automation components  
3. **PostSync** validates EventListener is responding
4. **Auto-heal** maintains configuration consistency

**Result**: Zero manual configuration after `make bootstrap`