# Generic Kubernetes Helm Charts

This collection provides production-ready Helm charts that can be deployed on **any Kubernetes cluster**.

## 📋 Charts Overview

### Infrastructure Charts (`infra-kube-*`)
- **`infra-kube-argocd`**: GitOps platform using official ArgoCD chart
- **`infra-kube-grafana`**: Observability dashboard with custom eBPF/AI dashboards  
- **`infra-kube-prometheus`**: Metrics collection and monitoring
- **`infra-kube-dashboard`**: Kubernetes Dashboard with external access
- **`infra-kube-registry`**: Container registry for private images
- **`infra-kube-sealed-secrets`**: Encrypted secrets management controller
- **`infra-kube-tekton`**: Complete CI/CD platform

### Application Charts (`app-kube-*`)
- **`app-kube-ebpf-ai`**: eBPF + AI Security monitoring application

## 🚀 Quick Start

### Prerequisites
- Kubernetes cluster (v1.26+)
- Helm v3.x
- Ingress Controller (NGINX, Traefik, etc.)

### Installation Steps

#### 1. Configure Global Settings
Create a `global-values.yaml` file:

```yaml
global:
  domain: "your-domain.com"  # Replace with your domain

# Storage class configuration (optional)
storageClass: "your-storage-class"  # Leave empty for default
```

#### 2. Install Infrastructure Charts
```bash
# Install in recommended order
helm install sealed-secrets ./infra-kube-sealed-secrets -f global-values.yaml
helm install prometheus ./infra-kube-prometheus -f global-values.yaml  
helm install grafana ./infra-kube-grafana -f global-values.yaml
helm install registry ./infra-kube-registry -f global-values.yaml
helm install dashboard ./infra-kube-dashboard -f global-values.yaml
helm install tekton ./infra-kube-tekton -f global-values.yaml
```

#### 3. Install Application Charts
```bash
# Configure container registries first
helm install ebpf-ai ./app-kube-ebpf-ai -f global-values.yaml \
  --set mlDetector.image.repository=your-registry/ml-detector \
  --set ebpfMonitor.image.repository=your-registry/ebpf-monitor
```

## ⚙️ Configuration

### Required Customizations

#### 1. Domain Configuration
Update `global.domain` in each chart's values.yaml or via global-values.yaml:
```yaml
global:
  domain: "apps.k8s.yourdomain.com"
```

#### 2. Container Images (for app charts)
Update image repositories in `app-kube-ebpf-ai/values.yaml`:
```yaml
mlDetector:
  image:
    repository: "your-registry/ml-detector"
    
ebpfMonitor:
  image:
    repository: "your-registry/ebpf-monitor"
```

#### 3. Storage Classes
Configure storage for persistent volumes:
```yaml
# In prometheus/values.yaml
prometheus:
  server:
    persistentVolume:
      storageClass: "your-storage-class"

# In registry/values.yaml  
persistence:
  storageClass: "your-storage-class"
```

#### 4. Ingress Class
Update ingress configuration for your cluster:
```yaml
ingress:
  className: "nginx"  # or "traefik", "istio", etc.
```

### Optional Customizations

#### Security (Production)
```yaml
# Disable insecure mode in ArgoCD
argo-cd:
  configs:
    params:
      "server.insecure": "false"
  server:
    insecure: false

# Use external secrets instead of sealed secrets
grafana:
  admin:
    existingSecret: "your-external-secret"
```

#### Resource Limits
```yaml
# Adjust resources based on cluster size
resources:
  limits:
    cpu: "1000m"
    memory: "2Gi"
  requests:
    cpu: "500m" 
    memory: "1Gi"
```

## 🔧 Chart-Specific Configuration

### ArgoCD
- **URL**: `https://argocd.{domain}`
- **Default**: Insecure mode (development)
- **Production**: Configure TLS and external authentication

### Grafana  
- **URL**: `https://grafana.{domain}`
- **Dashboards**: Includes eBPF/AI specific dashboards
- **Datasource**: Auto-configured for Prometheus

### Prometheus
- **Retention**: 30 days default
- **Storage**: 5Gi default
- **Targets**: Auto-discovery via ServiceMonitor

### Container Registry
- **URL**: `https://registry.{domain}`
- **Storage**: 15Gi default
- **Auth**: Basic authentication supported

### Tekton
- **Dashboard**: `https://tekton-dashboard.{domain}`
- **Webhooks**: `https://tekton-webhook.{domain}`
- **Components**: Pipelines + Dashboard + Triggers

## 🏗️ Architecture Compatibility

### Tested Platforms
- ✅ **Vanilla Kubernetes** (kubeadm, kops, etc.)
- ✅ **Managed Kubernetes** (EKS, GKE, AKS)
- ✅ **OpenShift** (with route configuration)
- ✅ **K3s/K3d** (lightweight clusters)
- ✅ **Minikube** (development)

### Storage Requirements
- **Default**: Uses cluster default storage class
- **Customizable**: Configure specific storage classes
- **Persistence**: All data persisted across restarts

### Networking Requirements  
- **Ingress Controller**: Required for external access
- **LoadBalancer**: Optional (can use NodePort)
- **DNS**: Configure DNS for your domain

## 🔒 Security

### Secrets Management
- **Sealed Secrets**: Encrypted secrets stored in Git
- **External Secrets**: Integrate with external secret managers
- **RBAC**: Minimal required permissions

### Network Policies
- **Default**: Permissive (development)
- **Production**: Enable network policies per chart

## 📚 Additional Resources

### Monitoring Stack
1. Install Prometheus → Grafana → Applications
2. Dashboards auto-import via ConfigMaps
3. Metrics collection via ServiceMonitors

### CI/CD Pipeline
1. Install Tekton platform
2. Configure Git webhooks
3. Create pipelines for your applications

### GitOps (Optional)
1. Install ArgoCD
2. Configure Git repositories  
3. Auto-sync applications

## 🐛 Troubleshooting

### Common Issues

#### DNS Resolution
```bash
# Test internal DNS
kubectl run test --image=busybox --rm -it --restart=Never -- nslookup prometheus-server.monitoring.svc.cluster.local
```

#### Storage Classes
```bash
# List available storage classes
kubectl get storageclass
```

#### Ingress Issues  
```bash
# Check ingress controller
kubectl get pods -n ingress-nginx
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

### Logs and Debugging
```bash
# Check pod status
kubectl get pods -A

# View logs
kubectl logs -n <namespace> <pod-name>

# Describe resources
kubectl describe ingress -n <namespace>
```

## 💡 Support

For issues or questions:
1. Check chart-specific README files
2. Review Kubernetes cluster compatibility
3. Verify domain and DNS configuration
4. Ensure storage classes are available

**All charts are designed to be generic and portable across different Kubernetes environments.**