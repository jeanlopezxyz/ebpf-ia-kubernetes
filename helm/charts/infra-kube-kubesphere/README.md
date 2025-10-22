# KubeSphere Integration for eBPF-AI Platform

This Helm chart integrates KubeSphere v3.4.1 multi-tenant container platform with the eBPF-AI Kubernetes cluster.

## Overview

KubeSphere provides:
- **Multi-tenant Management**: Project isolation and resource quotas
- **DevOps Pipeline**: Jenkins-based CI/CD integration
- **Application Store**: Helm-based application marketplace  
- **Observability**: Integrated monitoring, logging, and alerting
- **Service Mesh**: Istio integration (disabled in this setup)
- **Storage Management**: Persistent volume and storage class management

## Architecture Integration

### Existing Stack Integration
- **Monitoring**: Connects to existing Prometheus at `prometheus-server.prometheus.svc.cluster.local:80`
- **Visualization**: Integrates with existing Grafana at `grafana.grafana.svc.cluster.local:3000`
- **Storage**: Uses existing `local-path` storage class
- **Ingress**: Deploys via NGINX Ingress at `kubesphere.apps.k8s.labjp.xyz`

### Network Configuration
- **CNI**: Compatible with existing Cilium eBPF CNI
- **Service Mesh**: Istio disabled to avoid conflicts with Cilium
- **Network Policies**: Disabled for lab environment compatibility

## Component Configuration

### Core Components
- **Console**: Web UI accessible via ingress
- **Redis**: 2Gi storage for caching and session management
- **MinIO**: 20Gi object storage for artifacts and logs
- **Metrics Server**: Kubernetes metrics collection

### Optional Components (Enabled)
- **DevOps**: Jenkins with 16Gi storage and 8Gi memory limit
- **Logging**: Log collection with 2 replicas and 20Gi storage
- **Alerting**: Alert management integration
- **Notification**: Multi-channel notification support
- **Application Store**: OpenPitrix application marketplace

### Disabled Components
- **OpenLDAP**: Using default authentication for lab environment
- **Service Mesh**: Disabled to use Cilium instead of Istio
- **Network Policies**: Disabled for simplified lab networking
- **GPU Monitoring**: Disabled (no GPU nodes in current setup)

## Access Information

### Default Credentials
- **URL**: https://kubesphere.apps.k8s.labjp.xyz
- **Username**: admin
- **Password**: P@88w0rd

### Command Line Access
```bash
# Check KubeSphere installation status
kubectl logs -n kubesphere-system -l app=ks-installer

# Get KubeSphere console URL
kubectl get svc -n kubesphere-system ks-console

# Check all KubeSphere resources
kubectl get all -n kubesphere-system
kubectl get all -n kubesphere-controls-system
```

## Installation Process

1. **CRDs Installation**: Custom Resource Definitions are installed first
2. **Core Installation**: Namespaces, RBAC, and installer deployment
3. **Configuration**: ClusterConfiguration triggers the installation
4. **Component Deployment**: KubeSphere installs all enabled components

The installation process can take 10-15 minutes to complete all components.

## Resource Requirements

### Minimum Requirements
- **CPU**: 4 cores available
- **Memory**: 8Gi available  
- **Storage**: 60Gi available (Redis 2Gi + MinIO 20Gi + Jenkins 16Gi + Logging 20Gi + Prometheus 20Gi)

### Actual Resource Allocation
- **Installer**: 100m CPU, 100Mi memory
- **Console**: 100m CPU, 100Mi memory
- **DevOps Jenkins**: 4Gi memory request, 8Gi limit
- **Logging**: 2 replicas for high availability

## Monitoring Integration

KubeSphere integrates with the existing monitoring stack:

```yaml
integration:
  prometheus:
    external: true
    endpoint: "http://prometheus-server.prometheus.svc.cluster.local:80"
  grafana:
    external: true  
    endpoint: "http://grafana.grafana.svc.cluster.local:3000"
```

## Security Configuration

- **Pod Security**: Non-root execution (uid 1000)
- **Capabilities**: Minimal capabilities, drop ALL by default
- **Authentication**: JWT-based with configurable session timeouts
- **Multi-Login**: Enabled for development convenience

## Troubleshooting

### Check Installation Status
```bash
# Monitor installation progress
kubectl logs -n kubesphere-system deploy/ks-installer -f

# Check component status
kubectl get clusterconfiguration ks-installer -o yaml

# Verify all pods are running
kubectl get pods -n kubesphere-system
kubectl get pods -n kubesphere-controls-system
```

### Common Issues
1. **Slow Installation**: KubeSphere installs many components, be patient
2. **Resource Constraints**: Ensure sufficient CPU/memory/storage
3. **Network Connectivity**: Check ingress and DNS resolution
4. **Storage Issues**: Verify `local-path` storage class is available

### Access via Port Forward (Alternative)
```bash
kubectl port-forward -n kubesphere-system svc/ks-console 30880:80
# Access via http://localhost:30880
```

## GitOps Management

This chart is managed via ArgoCD GitOps:
- **Repository**: https://github.com/jeanlopezxyz/ebpf-ia-kubernetes.git
- **Path**: helm/charts/infra-kube-kubesphere
- **Sync Policy**: Automated with self-heal
- **ArgoCD Application**: `kubesphere` in `gitops` namespace

Updates to the chart configuration will automatically trigger ArgoCD synchronization.