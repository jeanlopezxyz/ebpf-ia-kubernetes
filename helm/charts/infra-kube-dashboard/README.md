# Kubernetes Dashboard Chart

Este chart instala el Kubernetes Dashboard oficial con configuración personalizada para el proyecto eBPF-AI.

## Descripción

El chart utiliza el Kubernetes Dashboard oficial como dependencia y agrega:
- Configuración personalizada para acceso externo vía Ingress
- Configuración de seguridad apropiada para entorno de desarrollo
- Integración con el stack de monitoreo eBPF-AI

## Componentes

### Chart Oficial (Dependencia)
- **kubernetes-dashboard**: v7.10.0 del repositorio oficial
- Incluye todos los recursos necesarios: Deployment, Service, RBAC, etc.

### Templates Personalizados
- **ingress.yaml**: Configuración de Ingress para acceso externo con NGINX

## Configuración

### Valores Principales

```yaml
kubernetes-dashboard:
  app:
    insecureLogin: true        # Permite login sin autenticación (desarrollo)
    enableSkipLogin: true      # Botón "Skip" en login
  service:
    type: ClusterIP           # Servicio interno (acceso vía Ingress)
  metricsScraper:
    enabled: true             # Habilita métricas de recursos

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: dashboard.apps.k8s.labjp.xyz
```

### Seguridad

#### Desarrollo vs Producción
- **Desarrollo**: `insecureLogin: true` para facilitar acceso
- **Producción**: Configurar autenticación RBAC apropiada

#### Acceso HTTPS
- El Dashboard utiliza HTTPS internamente
- Ingress configurado con `ssl-passthrough: true`
- Certificados manejados automáticamente por el Dashboard

## Acceso

### URL Externa
- **Dashboard**: https://dashboard.apps.k8s.labjp.xyz

### Acceso Local (desarrollo)
```bash
kubectl port-forward -n kubernetes-dashboard svc/kubernetes-dashboard 8443:443
```
Luego acceder a: https://localhost:8443

## Troubleshooting

### Problemas Comunes

1. **Error de certificado**
   - Verificar configuración SSL en Ingress
   - El Dashboard genera certificados automáticamente

2. **Métricas no disponibles**
   - Verificar que `metricsScraper.enabled: true`
   - Comprobar que metrics-server está funcionando en el cluster

3. **Acceso negado**
   - Para desarrollo: verificar `enableSkipLogin: true`
   - Para producción: configurar ServiceAccount con permisos apropiados

### Comandos Útiles

```bash
# Ver estado del Dashboard
kubectl get all -n kubernetes-dashboard

# Ver logs del Dashboard
kubectl logs -n kubernetes-dashboard deployment/kubernetes-dashboard

# Verificar Ingress
kubectl get ingress -n kubernetes-dashboard
```

## Dependencias

- **NGINX Ingress Controller**: Para acceso externo
- **Metrics Server**: Para métricas de recursos (opcional)
- **Kubernetes Dashboard Official Chart**: v7.10.0