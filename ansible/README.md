# Ansible Infrastructure Automation

Este directorio contiene la automatización Ansible para el despliegue de la infraestructura eBPF + AI GitOps.

## 🏗️ Estructura

```
ansible/
├── bootstrap.yml           # Playbook principal de instalación
├── cleanup.yml            # Playbook de limpieza/teardown
├── group_vars/
│   └── all.yml            # Variables de configuración global
├── inventory/
│   └── localhost.yml      # Inventario local
└── roles/                 # Roles funcionales
    ├── access-info/       # Muestra información de acceso
    ├── argocd/           # Instala ArgoCD GitOps
    ├── cilium/           # Instala Cilium CNI con eBPF
    ├── kubeadm/          # Instala Kubernetes con kubeadm
    ├── nginx-ingress/    # Instala NGINX Ingress Controller
    ├── prerequisites/    # Instala dependencias del sistema
    └── storage/          # Configura storage classes
```

## 🚀 Uso

### Instalación completa
```bash
make bootstrap          # Instala toda la infraestructura
```

### Comandos individuales
```bash
# Prerequisitos y cluster base
ansible-playbook -i inventory/localhost.yml bootstrap.yml

# Limpieza completa
ansible-playbook -i inventory/localhost.yml cleanup.yml
```

## ⚙️ Configuración

### Variables principales (`group_vars/all.yml`)
- **deployment_mode**: `lab` o `prod`
- **cluster_method**: `kubeadm` (único método soportado)
- **kubeadm**: Configuración del cluster
- **network**: Configuración de red y load balancer

### Modos de despliegue
- **Lab Mode**: NodePort + acceso directo via IP
- **Prod Mode**: NodePort + Load Balancer externo (pfSense)

## 🔄 Flujo de instalación

1. **prerequisites** - Instala Docker, Helm, kubectl
2. **kubeadm** - Crea cluster Kubernetes single-node
3. **cilium** - Instala CNI con eBPF (sin Gateway API)
4. **nginx-ingress** - Instala Ingress Controller
5. **storage** - Configura local-path storage
6. **argocd** - Instala GitOps con App-of-Apps pattern
7. **access-info** - Muestra URLs y credenciales

## 📝 Notas

- Todos los roles están probados y son funcionales
- Gateway API fue removido por conflictos con NGINX
- Las aplicaciones se despliegan via ArgoCD GitOps
- Compatible con HAProxy external load balancer