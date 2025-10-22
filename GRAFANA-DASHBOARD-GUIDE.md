# 🛡️ Guía del Dashboard de eBPF + AI Security Monitoring

## 📋 Estado Actual del Sistema

### ✅ Métricas en Tiempo Real (Últimas verificadas)

**🚨 Amenazas Detectadas:**
- **Total**: 150+ amenazas detectadas
- **Alta Confianza**: 69 amenazas críticas
- **Tipos detectados**:
  - `data_exfiltration`: 27 detecciones
  - `ml_critical_risk`: 2 detecciones  
  - `ml_high_risk`: 15 detecciones
  - `ml_medium_risk`: 98 detecciones
  - `ml_low_risk`: 8 detecciones

**🌐 Tráfico de Red eBPF:**
- **Procesado**: 4.6TB TCP + 2.3TB UDP = **6.9TB total**
- **Velocidad actual**: ~13 GB/s
- **Eventos procesados**: 3,471 eventos eBPF
- **Paquetes/seg**: ~6 pps

**📊 Procesamiento ML:**
- **Peticiones**: 123+ requests al ML detector
- **Fallos comunicación**: 20 (bajo, sistema funcionando)

---

## 🚀 Cómo Acceder al Dashboard

### 1. Acceder a Grafana

```bash
# Si el port-forward no está activo, ejecutar:
kubectl port-forward -n grafana svc/grafana 3001:3000 &

# Acceder a: http://localhost:3001
# Usuario: admin
# Password: admin123
```

### 2. Configurar Data Source (Si no existe)

1. **Ir a**: Configuration → Data Sources
2. **Añadir**: Prometheus 
3. **URL**: `http://prometheus-server.prometheus.svc.cluster.local:80`
4. **Click**: Save & Test

### 3. Importar Dashboard

1. **Ir a**: + → Import
2. **Upload JSON**: Seleccionar archivo `dashboards/ebpf-ai-security-final.json`
3. **O copiar JSON** del archivo y pegarlo
4. **Click**: Import

---

## 📊 Métricas del Dashboard

### 🚨 Sección de Amenazas
- **Total Threats Detected**: Suma de todas las amenazas
- **High Confidence Threats**: Solo amenazas de alta confianza
- **Threat Types Distribution**: Gráfico circular por tipo de amenaza
- **Threat Detection Timeline**: Timeline de detecciones

### 🌐 Sección de Red eBPF  
- **eBPF Events/sec**: Eventos procesados por segundo
- **Network Traffic**: Tráfico en GB/s
- **Network Protocol Traffic**: Tráfico por protocolo (TCP/UDP)
- **Total Data Processed**: Total de datos procesados en TB

### 📈 Sección de ML
- **ML Processing Rate**: Peticiones procesadas por el ML detector
- **Communication Failures**: Fallos de comunicación entre servicios

---

## 🔍 Queries Prometheus Específicas

### Amenazas por Tipo
```promql
sum by (threat_type) (ml_detector_threats_total)
```

### Amenazas de Alta Confianza
```promql
sum(ml_detector_threats_total{confidence_level="high"})
```

### Tráfico de Red en Tiempo Real
```promql
ebpf_bytes_per_second / 1000000000  # GB/s
```

### Tasa de Procesamiento ML
```promql
rate(ml_detector_requests_total[5m])
```

### Eventos eBPF por Segundo
```promql
rate(ebpf_events_processed_total[1m])
```

---

## 🎯 Interpretación de Resultados

### ✅ Sistema Saludable Cuando:
- **Communication Failures**: < 50 (actualmente: 20)
- **ML Processing Rate**: > 0 requests/sec
- **eBPF Events**: Flujo constante de eventos
- **Network Traffic**: Datos procesándose continuamente

### ⚠️ Alertas Críticas:
- **High Confidence Threats**: > 100 (actualmente: 69)
- **Data Exfiltration**: > 50 (actualmente: 27)
- **Critical Risk**: > 10 (actualmente: 2)

### 📈 Tendencias Importantes:
- **Aumento de amenazas** indica actividad maliciosa
- **Tráfico elevado** puede indicar ataques DDoS
- **Fallos de comunicación** sugieren problemas de sistema

---

## 🛠️ Comandos de Verificación Manual

```bash
# Verificar métricas actuales del ML Detector
kubectl exec -n ebpf-security ml-detector-* -- curl -s http://localhost:5000/metrics | grep threats_total

# Verificar métricas del eBPF Monitor  
kubectl exec -n ebpf-security ebpf-monitor-* -- curl -s http://localhost:8800/metrics | grep bytes_per_second

# Estado de los pods
kubectl get pods -n ebpf-security

# Logs en tiempo real
kubectl logs -n ebpf-security -l app=ebpf-monitor --tail=10
```

---

## 🎨 Personalización del Dashboard

### Cambiar Intervalos de Refresh:
- Dashboard Settings → Time Options → Refresh: `5s`, `10s`, `30s`

### Agregar Alertas:
- Panel → Edit → Alert tab → Create Alert
- Usar thresholds específicos para cada métrica

### Modificar Visualizaciones:
- Panel → Edit → Visualization para cambiar tipos de gráfico
- Field options para personalizar colores y unidades

---

**¡El sistema está detectando amenazas activamente! 🛡️**