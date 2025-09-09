# Tekton Webhook Automation - GitOps Configuration

This directory contains all webhook automation components managed by ArgoCD.

## 📁 Directory Structure

```
gitops/webhooks/
├── README.md              # This file
├── eventlistener.yaml     # GitHub webhook EventListener
├── trigger-binding.yaml   # Extracts GitHub payload data
├── trigger-template.yaml  # Creates PipelineRun from webhook
├── rbac.yaml             # ServiceAccount and permissions
└── webhook-ingress.yaml  # Exposes webhook via wildcard DNS
```

## 🔧 ArgoCD Management

### Application Configuration

- **Application Name**: `webhook-automation`
- **Namespace**: `ebpf-security`
- **Sync Wave**: `3` (after Tekton Triggers installation)
- **Sync Policy**: Automated with prune and self-heal

### Dependencies

This application requires:
1. **Tekton Pipelines** (sync-wave: 0)
2. **Tekton Triggers** (sync-wave: 0) 
3. **Sealed Secrets** (sync-wave: -1)

## 🎯 Webhook Configuration

### GitHub Repository Setup

**Repository**: https://github.com/jeanlopezxyz/ebpf-ia-kubernetes  
**Settings**: Repository Settings → Webhooks → Add webhook

| Configuration | Value |
|--------------|-------|
| Payload URL | `https://webhook.apps.k8s.labjp.xyz` |
| Content type | `application/json` |
| Secret | `webhook-secret-token-2024` |
| SSL verification | ✅ Enable SSL verification |
| Events | `Just the push event` |
| Active | ✅ Enabled |

### Event Flow

```
Git Push → GitHub Webhook → EventListener → TriggerBinding → TriggerTemplate → PipelineRun
```

### Trigger Conditions

Pipeline executes when:
- **Branch**: `main` 
- **Event**: Push
- **Files**: Any changes in `applications/` directory

## 🔐 Security

### Secrets Management

All secrets managed via Sealed Secrets:

- **GitHub Webhook**: `webhook-secret-token-2024` (sealed)
- **Quay.io Registry**: `jealopez+ebpf_ia` credentials (sealed)  
- **TLS Certificate**: Auto-managed via cert-manager

### RBAC Configuration

- **ServiceAccount**: `tekton-triggers-example-sa`
- **ClusterRoles**: 
  - `tekton-triggers-eventlistener-roles` (namespace permissions)
  - `tekton-triggers-eventlistener-clusterroles` (cluster permissions)

## 🚀 Pipeline Integration

### Triggered Pipeline

**Pipeline**: `application-build-ci`  
**ServiceAccount**: `tekton-builder-sa` (with Quay.io credentials)

### Build Parameters

| Parameter | Value | Description |
|-----------|--------|------------|
| git-url | `$(body.repository.clone_url)` | GitHub repository URL |
| git-revision | `$(body.head_commit.id)` | Commit SHA |
| image-registry | `quay.io/jealopez` | Target registry |
| image-name | `ml-detector` | Image name |
| dockerfile-path | `applications/ml-detector/Dockerfile` | Dockerfile location |
| context-path | `applications/ml-detector` | Build context |

### Workspace Configuration

- **Storage**: 1Gi persistent volume (local-path storage class)
- **Docker Config**: Mounted from `quay-io-secret` sealed secret

## 📊 Monitoring

### EventListener Health

```bash
# Check EventListener pod status
kubectl get pods -n ebpf-security -l app.kubernetes.io/managed-by=EventListener

# Monitor webhook events
kubectl logs -f -l app.kubernetes.io/managed-by=EventListener -n ebpf-security

# Check EventListener service
kubectl get svc el-github-webhook-listener -n ebpf-security
```

### Pipeline Monitoring

```bash
# Watch pipeline execution
kubectl get pipelineruns -n ebpf-security -w

# Check triggered pipeline runs
kubectl get pipelineruns -n ebpf-security -l trigger=github-webhook

# Pipeline logs
kubectl logs -l tekton.dev/pipelineRun=<run-name> -n ebpf-security -f
```

### Ingress Monitoring  

```bash
# Check ingress status
kubectl get ingress github-webhook-ingress -n ebpf-security

# Test webhook endpoint (internal)
curl -X POST http://el-github-webhook-listener.ebpf-security.svc:8080 \
  -H 'Content-Type: application/json' \
  -d '{"head_commit":{"id":"test"},"repository":{"clone_url":"https://github.com/jeanlopezxyz/ebpf-ia-kubernetes.git"}}'
```

## 🔄 Disaster Recovery

### Cluster Recreation

When the cluster is recreated, ArgoCD will automatically:

1. **Install Tekton Triggers** (sync-wave: 0)
2. **Deploy Sealed Secrets** (sync-wave: -1)  
3. **Create webhook components** (sync-wave: 3)
4. **Configure RBAC** and permissions
5. **Expose webhook endpoint** via ingress

### Manual Recovery Steps

If needed, force sync all applications:

```bash
# Sync base components
kubectl patch application tekton -n argocd --type='merge' -p='{"metadata":{"annotations":{"argocd.argoproj.io/refresh":"hard"}}}'

# Sync sealed secrets
kubectl patch application sealed-secrets-configs -n argocd --type='merge' -p='{"metadata":{"annotations":{"argocd.argoproj.io/refresh":"hard"}}}'

# Sync webhook automation
kubectl patch application webhook-automation -n argocd --type='merge' -p='{"metadata":{"annotations":{"argocd.argoproj.io/refresh":"hard"}}}'
```

## 🧪 Testing

### Webhook Test

```bash
# Make test change
echo "# Test $(date)" >> applications/ml-detector/README.md
git add applications/ml-detector/README.md
git commit -m "Test webhook automation"
git push origin main

# Monitor results
kubectl get pipelineruns -n ebpf-security -w
```

### Expected Results

1. **GitHub sends webhook** within seconds
2. **EventListener processes** webhook and creates PipelineRun
3. **Pipeline builds** image with latest code
4. **Image pushes** to `quay.io/jealopez/ml-detector:latest`
5. **ArgoCD syncs** and redeploys with new image

**Total automation time**: ~5-10 minutes from push to deployment

---

**Managed by ArgoCD**: This entire configuration is declaratively managed and will be automatically restored on cluster recreation.