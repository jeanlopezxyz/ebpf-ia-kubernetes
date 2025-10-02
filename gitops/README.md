# GitOps Configuration - eBPF + AI Security Platform

Clean and organized GitOps configuration using ArgoCD App-of-Apps pattern.

## 📁 Directory Structure

```
gitops/
├── app-of-apps.yaml           # Root ArgoCD application
└── applications/              # Clean application definitions
    ├── ebpf-ai.yaml          # Core: ML Detector + eBPF Monitor  
    ├── sealed-secrets.yaml   # Infrastructure: Sealed Secrets controller
    ├── grafana.yaml          # Monitoring: Grafana dashboards
    ├── prometheus.yaml       # Monitoring: Prometheus metrics
    ├── registry.yaml         # Infrastructure: Container registry
    ├── kubernetes-dashboard.yaml # Infrastructure: K8s dashboard
    └── tekton.yaml           # CI/CD: Tekton pipelines
```

## 🎯 Design Principles

### 1. Single Responsibility
- **One application** per major component
- **One directory** per application
- **No fragmentation** or resource sharing

### 2. Helm Integration
- **Credentials**: `helm/charts/sealed-secrets-configs/`
- **Applications**: `helm/charts/ebpf-ai/`  
- **Infrastructure**: `helm/charts/[component]/`

### 3. Sync Wave Ordering
- **Wave -1**: `sealed-secrets` (controller)
- **Wave 0**: `tekton`, `tekton-automation-complete` (platform)
- **Wave 1**: `sealed-secrets-configs` (credentials)
- **Wave 2**: `ebpf-ai` (applications)

## 🔧 ArgoCD Applications

| Application | Purpose | Source Type | Sync Wave |
|-------------|---------|-------------|-----------|
| `sealed-secrets` | Sealed Secrets controller | Helm (external) | -1 |
| `sealed-secrets-configs` | Encrypted credentials | Helm (local) | 1 |
| `tekton` | Tekton Pipelines | Helm (external) | 0 |
| `tekton-automation-complete` | Tekton Triggers + Webhooks | Directory (local) | 0 |
| `ebpf-ai` | Main application stack | Helm (local) | 2 |

## 🚀 Benefits

### Cluster Recreation
- **Complete automation** via App-of-Apps pattern
- **Proper ordering** via sync waves
- **Zero manual steps** after bootstrap

### Maintenance
- **Clear separation** of concerns
- **Easy updates** via Helm values
- **Rollback capability** via ArgoCD

### Security  
- **All secrets encrypted** via Sealed Secrets
- **RBAC separation** per component
- **No plaintext credentials** in Git

## 📋 Usage

### Deploy Changes
```bash
# Update application code
git add applications/
git commit -m "Update ML detector"
git push origin main

# GitHub webhook → Tekton → Quay.io → ArgoCD → Deploy
```

### Update Credentials  
```bash
# Rotate sealed secrets via Helm values
helm template sealed-secrets-configs helm/charts/sealed-secrets-configs/
# Commit updated sealed secrets
```

### Monitor Applications
```bash
# Watch ArgoCD applications
kubectl get applications -n argocd -w

# Check specific application
kubectl describe application tekton-automation-complete -n argocd
```