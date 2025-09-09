# Backstage Configuration for eBPF + AI Security Platform

This directory contains all Backstage-related configurations for the eBPF + AI Security Platform.

## 📁 Directory Structure

```
backstage/
├── docs/                          # Documentation and service catalog
│   ├── catalog-info.yaml           # Main service catalog definitions
│   ├── index.md                    # Platform overview documentation
│   ├── mkdocs.yml                  # TechDocs configuration
│   └── security/                   # Security-specific documentation
│       ├── architecture/           # Security architecture guides
│       ├── procedures/             # Incident response, monitoring
│       ├── compliance/             # CIS controls, NIST framework
│       └── templates/              # Documentation templates
├── templates/                      # Scaffolding templates
│   ├── ebpf-detector/              # eBPF security detector template
│   └── ml-model/                   # ML security model template
├── catalog/                        # Catalog management
│   └── catalog-info.yaml           # Catalog location reference
├── config/                         # Backstage configuration
│   └── backstage-config.yaml       # Main Backstage app configuration
└── README.md                       # This file
```

## 🚀 Features Configured

### 1. Service Discovery & Catalog
- **AI Threat Detector** (ML-based threat detection)
- **eBPF Monitor** (Kernel-level network monitoring)
- **Security Dashboard** (Grafana integration)
- **APIs** (Detection and metrics endpoints)
- **Teams** (Security, AI, eBPF, Security Ops)

### 2. Security Documentation Hub
- **Architecture guides** for security implementation
- **Incident response** procedures
- **Compliance documentation** (CIS Controls)
- **TechDocs integration** with MkDocs

### 3. Developer Templates
- **eBPF Detector Template**: Create new security detectors
- **ML Model Template**: Develop threat detection models
- **Automated scaffolding** for security components

### 4. CI/CD Integration
- **GitHub webhook** integration for automatic catalog refresh
- **Tekton pipeline** triggers for automated deployments
- **GitOps workflows** for security policy management

## 🔧 Configuration

### Access URLs:
- **Backstage Portal**: https://backstage.apps.k8s.labjp.xyz
- **GitHub Webhook**: https://backstage.apps.k8s.labjp.xyz/api/catalog/refresh

### Deployment:
- Managed by **ArgoCD** via `helm/charts/backstage/`
- Automatic deployment during `make bootstrap`
- Configuration in `backstage/config/backstage-config.yaml`

## 📝 Usage

### Adding New Services:
1. Add component to `backstage/docs/catalog-info.yaml`
2. Git push triggers automatic catalog refresh
3. Service appears in Backstage portal

### Creating New Security Components:
1. Use **CREATE** button in Backstage
2. Select **eBPF Detector** or **ML Model** template
3. Fill parameters and generate scaffolding
4. Automated CI/CD deployment via Tekton

### Documentation:
- Edit files in `backstage/docs/security/`
- TechDocs automatically builds and publishes
- Available in Backstage portal under **Docs** section