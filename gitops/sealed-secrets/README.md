# Sealed Secrets for eBPF-AI Platform

Este directorio contiene los Sealed Secrets específicos para el proyecto eBPF-AI.

## Descripción

Los Sealed Secrets permiten almacenar secretos encriptados en Git de forma segura. Solo el controlador de Sealed Secrets en el cluster puede desencriptarlos.

## Secretos Incluidos

### 1. ArgoCD Admin Secret
- **Archivo**: `argocd-admin-secret.yaml`
- **Namespace**: `argocd`
- **Propósito**: Credenciales de administrador para ArgoCD
- **Campos**: `admin-user`, `admin-password`

### 2. Grafana Admin Secret
- **Archivo**: `grafana-admin-secret.yaml`
- **Namespace**: `grafana`
- **Propósito**: Credenciales de administrador para Grafana
- **Campos**: `admin-user`, `admin-password`

### 3. GitHub Webhook Secret
- **Archivo**: `github-webhook-secret.yaml`
- **Namespace**: `tekton`
- **Propósito**: Secret para validar webhooks de GitHub
- **Campos**: `webhook-secret`

### 4. Quay Registry Secret
- **Archivo**: `quay-registry-secret.yaml`
- **Namespace**: `ebpf-security`
- **Propósito**: Credenciales para registry Quay.io
- **Tipo**: `kubernetes.io/dockerconfigjson`

## Uso

### Aplicar Sealed Secrets
```bash
kubectl apply -f gitops/sealed-secrets/
```

### Verificar Secretos Desencriptados
```bash
kubectl get secrets -n argocd argocd-admin-secret
kubectl get secrets -n grafana grafana-admin-secret
kubectl get secrets -n tekton github-webhook-secret
kubectl get secrets -n ebpf-security quay-registry-secret
```

## Regenerar Sealed Secrets

Si necesitas regenerar algún sealed secret:

1. Instala `kubeseal` CLI
2. Obtén la clave pública del controlador:
   ```bash
   kubeseal --fetch-cert > public.pem
   ```
3. Crea un secret normal y encríptalo:
   ```bash
   echo -n mypassword | kubectl create secret generic mysecret --dry-run=client --from-file=password=/dev/stdin -o yaml | kubeseal -o yaml > mysealedsecret.yaml
   ```

## Dependencias

Este directorio requiere que el controlador de Sealed Secrets esté instalado en el cluster a través del chart `infra-kube-sealed-secrets`.

## Valores de Referencia

Para desarrollo y documentación, los valores originales están comentados en cada archivo (pero no deben usarse en producción).