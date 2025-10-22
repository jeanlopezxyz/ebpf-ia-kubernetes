# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is an eBPF + AI GitOps platform implementing a complete infrastructure-as-code solution. The system combines eBPF network monitoring with AI-based threat detection, managed entirely through GitOps patterns.

### Core Components:
- **Ansible Bootstrap** - Day-0 infrastructure setup with kubeadm+KVM, Cilium CNI, ArgoCD
- **ArgoCD GitOps** - Declarative application management using App-of-Apps pattern  
- **Tekton CI/CD** - Automated image building and deployment pipelines
- **eBPF Applications** - ML Detector (Python) and eBPF Monitor (Go) for security monitoring
- **Gateway API** - Modern ingress management with Cilium Gateway and HTTPRoute support

## Essential Commands

### Infrastructure Management
```bash
make bootstrap          # Complete kubeadm+KVM infrastructure setup (15-20 min)
make status            # Health check across all components  
make clean             # Teardown entire environment
make sync              # Force ArgoCD application synchronization
make port-forward      # Local access to services (ArgoCD:8080, Grafana:3000)
make test              # Basic functionality validation
make info              # Show all access URLs and credentials
```

### Development Workflow
```bash
# Deploy changes (automated via GitHub webhook)
git add . && git commit -m "description" && git push origin main
# GitHub webhook triggers Tekton pipeline automatically
# Pipeline builds image and pushes to Quay.io
# ArgoCD auto-syncs new image within 3 minutes, or force with:
make sync

# Webhook automation for applications/ changes:
# Git Push → GitHub Webhook → Tekton → Quay.io → ArgoCD → Deploy

# Development environment with hot-reload
make dev                # Setup development environment with auto-sync

# Code quality checks (before committing)
make lint-code          # Lint Python (ruff, black) and Go (golangci-lint)
make lint-helm          # Lint all Helm charts
make test               # Run basic functionality tests

# Access services
kubectl port-forward svc/argocd-server -n argocd 8080:80
kubectl port-forward svc/kube-prometheus-stack-grafana -n monitoring 3000:80

# Check pipeline status
kubectl get pipelineruns,taskruns -n ebpf-security
kubectl get applications -n argocd
```

### Debugging Commands
```bash
# Check cluster status
kubectl get nodes
kubectl get pods -A
kubectl get applications -n argocd

# Application logs
make logs               # View ML Detector and eBPF Monitor logs
kubectl logs -n ebpf-security -l app=ml-detector --tail=20
kubectl logs -n ebpf-security -l app=ebpf-monitor --tail=20

# Pipeline debugging
kubectl describe pipelinerun <name> -n ebpf-security
kubectl logs <pod-name> -n ebpf-security

# ArgoCD debugging  
kubectl describe application ebpf-ai -n argocd
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller

# Port forwarding management
make port-forward       # Setup all service port forwards
make port-stop          # Stop all port forwards
make port-status        # Show active port forwards
```

## Configuration Architecture

### Environment Modes
The system supports two deployment modes via `ansible/group_vars/all.yml`:

**Lab Mode (default):**
```yaml
deployment_mode:
  type: "lab"
```
- NodePort services
- Podman driver  
- Simplified networking (no external load balancer)
- Access via: `http://node-ip:nodeport`

**Production Mode:**
```yaml
deployment_mode:
  type: "prod"  
  external_lb: true
```
- NodePort services with external load balancer (pfSense HAProxy)
- QEMU driver with bridge networking
- Real network IPs for direct access

### Key Configuration Files
- **`ansible/group_vars/all.yml`** - Environment settings, network config, resource limits
- **`helm/charts/app-kube-ebpf-ai/values.yaml`** - Main eBPF+AI application configuration
- **`helm/charts/infra-kube-*/values.yaml`** - Infrastructure component configurations (ArgoCD, Grafana, Prometheus, etc.)
- **`gitops/applications/`** - ArgoCD application definitions with sync policies

## Application Structure

### ML Detector (`applications/ml-detector/`)
Python Flask application providing AI-based threat detection:
- **Endpoints**: `/health`, `/metrics`, `/detect`
- **Dependencies**: Redis for caching, Prometheus for metrics
- **Configuration**: Via Helm values and environment variables
- **Models**: Statistical, spatial, temporal anomaly detection models
- **Rules**: Network, process monitoring, user behavior rules
- **Development**: `cd applications/ml-detector && python app.py`
- **Testing**: `cd applications/ml-detector && python -m pytest tests/`

### eBPF Monitor (`applications/ebpf-monitor/`)  
Go application for eBPF-based network monitoring:
- **Endpoints**: `/health`, `/metrics`
- **Function**: Collects network metrics, integrates with ML Detector
- **Build**: Standard Go modules with CGO enabled for eBPF
- **Components**: Network monitor (eBPF), QoS calculator, Prometheus metrics
- **Development**: `cd applications/ebpf-monitor && go run cmd/monitor/main.go`

## CI/CD Pipeline Architecture

### Pipeline Flow
1. **Git Push** → Tekton detects changes
2. **fetch-source** → Clone repository
3. **generate-tag** → Create semantic version tag
4. **build-image** → Buildah constructs container image
5. **sync-deploy** → Trigger ArgoCD sync

### Image Management
- **Registry**: Internal container registry (port 5000 via registry chart)
- **Tagging**: Semantic versioning with `v$major.$minor.$patch`  
- **Storage**: Persistent via PVC, configurable storage class

## GitOps Patterns

### App-of-Apps Structure
```
ebpf-ai-apps (root)
├── ebpf-ai (main application)
├── tekton-pipelines (CI/CD platform)
├── tekton-ci-pipelines (pipeline definitions)
└── monitoring stack (Prometheus/Grafana)
```

### Sync Policies
- **Automated sync** with prune and self-heal
- **Retry logic** with exponential backoff
- **CreateNamespace** enabled for dynamic namespace creation

## Networking and Access

### Service Access Patterns
- **Gateway API**: Modern ingress with Cilium Gateway and HTTPRoute resources
- **NGINX Ingress**: Traditional ingress routes `/argocd`, `/grafana`, `/dashboard`
- **NodePort**: Direct service access for development
- **External Load Balancer**: pfSense HAProxy managed access in production mode

### Default Credentials
- **ArgoCD**: admin/[sealed-secret-generated]
- **Grafana**: admin/[sealed-secret-generated]
- **Credentials**: Check `gitops/sealed-secrets/README.md` for generated passwords

### GitHub Webhook Automation
- **Webhook URL**: https://webhook.apps.k8s.labjp.xyz
- **Secret**: [sealed-secret] (see sealed-secrets/README.md)
- **Trigger**: Push events to main branch with applications/ changes
- **Flow**: GitHub → Webhook → Tekton → Quay.io → ArgoCD → Deploy
- **Documentation**: `docs/WEBHOOK-AUTOMATION.md`

## Development Notes

### Helm Chart Dependencies
The main application chart requires dependency builds:
```bash
cd helm/charts/app-kube-ebpf-ai && helm dependency build
```

### Chart Architecture
The project uses a modular Helm chart approach:
- **`infra-kube-*`** charts: Infrastructure components (ArgoCD, Grafana, Prometheus, Registry, etc.)
- **`app-kube-*`** charts: Application-specific components (eBPF+AI security monitoring)
- All charts are designed to be portable across different Kubernetes clusters

### ArgoCD Application Debugging
When applications show `OutOfSync` or `Degraded`:
1. Check application details: `kubectl describe application <name> -n argocd`
2. Look for template errors in Helm charts
3. Verify namespace existence and RBAC permissions
4. Force refresh: `kubectl patch application <name> -n argocd --type='merge' -p='{"metadata":{"annotations":{"argocd.argoproj.io/refresh":"hard"}}}'`

### Tekton Pipeline Troubleshooting
For pipeline failures:
1. Check feature flags are enabled: `kubectl get configmap feature-flags -n tekton-pipelines`
2. Verify tasks exist in target namespace: `kubectl get tasks -n ebpf-security`
3. Check workspace permissions and PVC binding
4. Validate API versions match between pipelines and tasks (use `tekton.dev/v1`)

### Common Issues and Solutions
- **ImagePullBackOff**: Images need to be built via Tekton pipelines first
- **Permission errors in pipelines**: Ensure `fsGroup: 65532` in securityContext
- **ArgoCD OutOfSync**: Often due to Helm template validation errors - check logs
- **Registry connectivity**: Use internal IP `192.168.67.2:5000` for in-cluster access

### Gateway API Configuration
The system supports modern Gateway API for ingress management:
- **Cilium Gateway**: Uses Cilium as the Gateway API implementation
- **HTTPRoute Resources**: Modern alternative to traditional Ingress resources
- **Deployment**: Automatically installed via `gateway-api-simple` Ansible role
- **Configuration**: Gateway and HTTPRoute templates in `helm/charts/infra-kube-*/templates/httproute.yaml`

### External Load Balancer Configuration (pfSense HAProxy)
For production deployments with external load balancer:
- **TCP Pass-through**: API access via port 6443 without SSL termination
- **SSL Termination**: Application access via ports 80/443 with Let's Encrypt certificates  
- **Fixed NodePorts**: 30080 (HTTP), 30443 (HTTPS), 30082 (GitHub Webhook) for stable configuration
- **VIP Configuration**: Dedicated Virtual IP for Kubernetes services

### Architecture Summary
The system prioritizes GitOps principles with everything managed declaratively through Git, automated CI/CD via Tekton, comprehensive observability through Prometheus/Grafana stack, and modern networking via Gateway API with Cilium CNI.