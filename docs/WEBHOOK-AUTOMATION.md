# GitHub Webhook + Tekton Pipeline Automation

Complete guide for automated CI/CD pipeline integration using GitHub webhooks with Tekton Triggers.

## 🎯 Overview

This document describes the complete automation flow:

```
GitHub Push → Webhook → Tekton Pipeline → Build Image → Push Quay.io → ArgoCD Deploy
```

## 🏗️ Architecture

### Components

1. **GitHub Webhook** - Sends events on repository changes
2. **Tekton EventListener** - Receives and processes webhook events  
3. **Tekton Pipeline** - Builds and pushes container images
4. **Sealed Secrets** - Secure credential management
5. **ArgoCD** - Declarative GitOps deployment

### Network Flow

```
GitHub → https://webhook.apps.k8s.labjp.xyz → EventListener → TriggerTemplate → PipelineRun
```

## 🔐 Security Configuration

### Sealed Secrets

All credentials are encrypted using Sealed Secrets:

- **Grafana Admin**: `MIVl6ww1DkKZidZyuHHXS5c4N` (encrypted in git)
- **ArgoCD Admin**: `oSsMYDYPSzcXXexpW2GdSrM2g` (encrypted in git)
- **Quay.io Robot**: `jealopez+ebpf_ia` + token (encrypted in git)

### GitHub Webhook Secret

- **Secret Token**: `webhook-secret-token-2024`
- **Purpose**: Validates webhook authenticity from GitHub
- **Location**: `gitops/sealed-secrets/github-webhook-secret-sealed.yaml`

## 📋 Configuration Files

### ArgoCD Applications

```yaml
# Core automation stack managed by ArgoCD
gitops/applications/
├── sealed-secrets.yaml              # Sealed Secrets controller (Helm)
├── sealed-secrets-configs.yaml      # Encrypted credentials
├── tekton-triggers-official.yaml    # Tekton Triggers from official repo
├── github-webhooks.yaml            # EventListener and webhook config
└── tekton-pipelines-custom.yaml    # Custom pipeline definitions
```

### Webhook Components

```yaml
# GitHub webhook automation
gitops/webhooks/
├── eventlistener.yaml      # Receives GitHub webhook events
├── trigger-binding.yaml    # Extracts data from GitHub payload  
├── trigger-template.yaml   # Creates PipelineRun from webhook
├── rbac.yaml              # ServiceAccount and permissions
├── webhook-secret.yaml    # GitHub webhook validation secret
└── webhook-ingress.yaml   # Exposes webhook via wildcard DNS
```

### Pipeline Configuration

```yaml
# Automated pipeline execution
gitops/pipelines/
├── application-build-ci.yaml    # Main build pipeline
├── quay-credentials.yaml        # Registry authentication (sealed)
├── pipeline-rbac.yaml          # Pipeline execution permissions
└── workspace-templates.yaml    # Shared workspace configurations
```

## 🚀 GitHub Webhook Setup

### 1. Repository Webhook Configuration

Navigate to: https://github.com/jeanlopezxyz/ebpf-ia-kubernetes/settings/hooks

**Add webhook with:**

| Field | Value |
|-------|-------|
| Payload URL | `https://webhook.apps.k8s.labjp.xyz` |
| Content type | `application/json` |
| Secret | `webhook-secret-token-2024` |
| SSL verification | ✅ Enable SSL verification |
| Events | `Just the push event` |
| Active | ✅ Enabled |

### 2. Event Filtering

The webhook automatically filters for:

- **Branch**: Only `main` branch pushes
- **Path**: Only changes in `applications/` directory
- **Event**: Push events only (not PR, issues, etc.)

### 3. Pipeline Trigger Conditions

Pipeline executes when:

```bash
# Push to main with changes in applications/
git add applications/ml-detector/some-file.py
git commit -m "Update ML detector"
git push origin main
```

**Result**: Automatic pipeline execution with image build and deployment.

## 🔧 Troubleshooting

### Common Issues

#### 1. EventListener Pod CrashLoopBackOff

**Symptom**: EventListener pod restarting continuously  
**Cause**: Missing or invalid caBundle for ClusterInterceptors  
**Solution**: 
```bash
# Reinstall Tekton Triggers completely
kubectl apply -f https://storage.googleapis.com/tekton-releases/triggers/latest/release.yaml
kubectl apply -f https://storage.googleapis.com/tekton-releases/triggers/latest/interceptors.yaml

# Verify core interceptors are running
kubectl get pods -n tekton-pipelines | grep interceptors
```

#### 2. GitHub Webhook Error 503

**Symptom**: "Last delivery was not successful. Invalid HTTP Response: 503"  
**Cause**: EventListener not responding (usually RBAC or interceptor issues)  
**Solution**:
```bash
# Check EventListener pod status
kubectl get pods -n ebpf-security -l app.kubernetes.io/managed-by=EventListener

# Check logs for specific error
kubectl logs -l app.kubernetes.io/managed-by=EventListener -n ebpf-security

# Apply official RBAC
kubectl apply -f https://raw.githubusercontent.com/tektoncd/triggers/main/examples/rbac.yaml
```

#### 3. Pipeline Not Triggered

**Symptom**: Webhook received but no PipelineRun created  
**Cause**: TriggerBinding or TriggerTemplate missing/misconfigured  
**Solution**:
```bash
# Check trigger components
kubectl get triggerbindings,triggertemplates -n ebpf-security

# Verify EventListener configuration
kubectl describe eventlistener github-webhook-listener -n ebpf-security

# Check recent events
kubectl get events -n ebpf-security --sort-by=.lastTimestamp | tail -10
```

#### 4. Image Build/Push Failures

**Symptom**: Pipeline runs but fails at build/push stage  
**Cause**: Incorrect ServiceAccount or missing Quay.io credentials  
**Solution**:
```bash
# Verify ServiceAccount has Quay.io credentials
kubectl get serviceaccount tekton-builder-sa -n ebpf-security -o yaml

# Check if sealed secret was applied
kubectl get secrets quay-io-secret -n ebpf-security

# Verify pipeline uses correct ServiceAccount
kubectl get pipelinerun <name> -o yaml | grep serviceAccountName
```

### Debug Commands

```bash
# Check overall webhook system health
kubectl get eventlisteners,triggerbindings,triggertemplates -n ebpf-security

# Monitor webhook events in real-time
kubectl logs -f -l app.kubernetes.io/managed-by=EventListener -n ebpf-security

# Test webhook manually (from within cluster)
kubectl run curl --rm -i --tty --restart=Never --image=curlimages/curl -- \
  curl -X POST http://el-github-webhook-listener.ebpf-security.svc:8080 \
  -H 'Content-Type: application/json' \
  -d '{"head_commit":{"id":"test123"},"repository":{"clone_url":"https://github.com/jeanlopezxyz/ebpf-ia-kubernetes.git"}}'

# Check pipeline execution
kubectl get pipelineruns -n ebpf-security -w
```

## 📊 Monitoring and Metrics

### EventListener Metrics

```bash
# EventListener exposes metrics on port 9000
kubectl port-forward svc/el-github-webhook-listener -n ebpf-security 9000:9000

# Access metrics
curl http://localhost:9000/metrics
```

### Pipeline Monitoring

```bash
# Watch pipeline execution
kubectl get pipelineruns -n ebpf-security -w

# Detailed pipeline logs
kubectl logs -l tekton.dev/pipelineRun=<run-name> -n ebpf-security -f

# Check task status
kubectl get taskruns -n ebpf-security
```

## 🎯 Expected Behavior

### Successful Webhook Flow

1. **Developer pushes** changes to `applications/` in main branch
2. **GitHub sends webhook** to `https://webhook.apps.k8s.labjp.xyz`
3. **EventListener receives** webhook and validates signature
4. **TriggerBinding extracts** commit SHA and repository URL
5. **TriggerTemplate creates** PipelineRun with parameters
6. **Pipeline executes**:
   - Fetches source code from GitHub
   - Builds container image with Buildah
   - Pushes to `quay.io/jealopez/ml-detector:latest`
   - Triggers ArgoCD sync
7. **ArgoCD detects** new image and redeploys automatically

### Timeline

| Step | Duration | Status Check |
|------|----------|--------------|
| Webhook → EventListener | < 1 second | EventListener logs |
| TriggerTemplate → PipelineRun | < 5 seconds | `kubectl get pipelineruns` |
| Source fetch | 10-30 seconds | Fetch task logs |
| Image build | 2-5 minutes | Build task logs |
| Image push | 30-60 seconds | Push task logs |
| ArgoCD sync | 1-3 minutes | `kubectl get applications` |
| Pod deployment | 1-2 minutes | `kubectl get pods` |

**Total automation time**: ~5-10 minutes from push to deployment

## 🔄 Maintenance

### Updating Webhook Secret

```bash
# Generate new secret
NEW_SECRET=$(openssl rand -base64 32)

# Update sealed secret
kubectl create secret generic github-webhook-secret \
  --from-literal=secretToken="$NEW_SECRET" \
  --namespace=ebpf-security \
  --dry-run=client -o yaml | kubeseal -o yaml > gitops/sealed-secrets/github-webhook-secret-sealed.yaml

# Update GitHub webhook configuration with new secret
# Commit and push the sealed secret
git add gitops/sealed-secrets/github-webhook-secret-sealed.yaml
git commit -m "Rotate GitHub webhook secret"
git push origin main
```

### Rotating Quay.io Credentials

```bash
# Create new robot token in Quay.io
# Update sealed secret
export QUAY_USERNAME="jealopez+ebpf_ia"
export QUAY_TOKEN="new-robot-token"

kubectl create secret docker-registry quay-io-secret \
  --docker-server=quay.io \
  --docker-username="$QUAY_USERNAME" \
  --docker-password="$QUAY_TOKEN" \
  --docker-email="pipeline@ebpf-ai.com" \
  --namespace=ebpf-security \
  --dry-run=client -o yaml | kubeseal -o yaml > gitops/sealed-secrets/quay-io-secret-sealed.yaml

git add gitops/sealed-secrets/quay-io-secret-sealed.yaml
git commit -m "Rotate Quay.io credentials"
git push origin main
```

## 📈 Performance Tuning

### Pipeline Optimization

```yaml
# Optimize pipeline for faster execution
spec:
  taskRunTemplate:
    serviceAccountName: tekton-builder-sa
    # Add resource limits for faster scheduling
    metadata:
      labels:
        pipeline.tekton.dev/performance: optimized
  params:
    # Cache optimization
    - name: BUILD_EXTRA_ARGS
      value: "--cache-from=type=registry,ref=quay.io/jealopez/ml-detector:cache"
```

### EventListener Resource Limits

```yaml
# EventListener with resource constraints
spec:
  resources:
    kubernetesResource:
      spec:
        template:
          spec:
            containers:
            - resources:
                requests:
                  memory: "64Mi"
                  cpu: "100m"
                limits:
                  memory: "128Mi"
                  cpu: "200m"
```

## 🛡️ Security Best Practices

### 1. Webhook Validation
- Always use secret validation for webhook authenticity
- Enable SSL verification in GitHub webhook settings
- Rotate webhook secrets regularly (quarterly recommended)

### 2. RBAC Principle of Least Privilege
- Use namespace-scoped permissions where possible
- Avoid cluster-admin unless absolutely necessary
- Regular RBAC audits

### 3. Image Security
- Use specific image tags instead of `latest` in production
- Enable image signature verification
- Regular base image updates for security patches

### 4. Network Security
- Use TLS/HTTPS for all webhook endpoints
- Implement network policies to restrict pod communication
- Monitor webhook endpoint for unusual traffic patterns

---

**Last Updated**: 2025-09-09  
**Tested Version**: Tekton Triggers v0.29.x  
**Kubernetes Version**: 1.33.4  
**Status**: Production Ready ✅