# ML Detector - Comprehensive Logging Implementation

## Overview

Se ha implementado logging detallado en la aplicación ML Detector para mostrar exactamente qué recibe, cómo procesa y cómo envía métricas a Prometheus.

## 🎯 Funcionalidades Implementadas

### 1. **Logging de Requests Recibidos**
- ✅ **Endpoint `/detect`**: Logs detallados de requests JSON
- ✅ **Endpoint `/metrics`**: Logs de scraping de Prometheus  
- ✅ **Endpoint `/detect/prom`**: Logs de consultas a Prometheus
- ✅ **Headers y Source IP**: Tracking completo de requests

### 2. **Logging de Procesamiento**
- ✅ **Validación de datos**: Success/error de parsing JSON
- ✅ **Feature extraction**: Logs de características extraídas
- ✅ **Model inference**: Resultados de detección
- ✅ **Threat analysis**: Confidence scores y tipos de amenaza

### 3. **Logging de Métricas Prometheus**
- ✅ **Metric generation**: Proceso de generación de payload
- ✅ **Metric updates**: Incremento de contadores específicos
- ✅ **Sample metrics**: Muestra de métricas generadas
- ✅ **Payload size**: Información de tamaño de datos

## 📊 Formato de Logs

### Estructura de Logs
```
TIMESTAMP - LOGGER_NAME - LEVEL - FUNCTION:LINE - MESSAGE
```

### Emojis para Categorización
- 📥 **RECEIVE**: Requests entrantes
- 📊 **REQUEST_DATA**: Datos del request
- 🔍 **REQUEST_HEADERS**: Headers HTTP
- 🌐 **REQUEST_SOURCE**: IP origen
- ✅ **VALIDATION**: Validación exitosa
- ❌ **VALIDATION_ERROR**: Errores de validación
- 🤖 **DETECTION**: Proceso de detección
- 🎯 **DETECTION_RESULT**: Resultados
- ⚠️ **THREAT_DETECTED**: Amenazas encontradas
- 📈 **CONFIDENCE**: Nivel de confianza
- 🏷️ **THREAT_TYPES**: Tipos de amenaza
- 📊 **PROMETHEUS_METRIC**: Métricas enviadas
- 📤 **RESPONSE**: Respuestas enviadas
- 🔗 **PROMETHEUS_CONNECTION**: Conexiones
- 📡 **PROMETHEUS_QUERY**: Consultas a Prometheus

## 🔧 Configuración Técnica

### Variables de Entorno
```bash
LOG_LEVEL=INFO                    # Nivel de logging
PYTHONUNBUFFERED=1               # Output inmediato
```

### Gunicorn Configuration
```python
# Logging to stdout/stderr for Kubernetes
accesslog = "-"
errorlog = "-"
loglevel = "info"
capture_output = True
enable_stdio_inheritance = True
```

## 📝 Ejemplos de Logs

### Request de Detección
```
2025-10-22 12:00:00 - api - INFO - detect_threat:54 - 📥 RECEIVE: /detect endpoint called
2025-10-22 12:00:00 - api - INFO - detect_threat:55 - 📊 REQUEST_DATA: {"packets": 1000, "bytes": 50000, "syn_packets": 100, "unique_ips": 10, "unique_ports": 5, "duration": 60}
2025-10-22 12:00:00 - api - INFO - detect_threat:56 - 🔍 REQUEST_HEADERS: {"Content-Type": "application/json", "User-Agent": "curl/7.81.0"}
2025-10-22 12:00:00 - api - INFO - detect_threat:57 - 🌐 REQUEST_SOURCE: 127.0.0.1
2025-10-22 12:00:00 - api - INFO - detect_threat:61 - ✅ VALIDATION: Request successfully validated
2025-10-22 12:00:00 - api - INFO - detect_threat:69 - 🤖 DETECTION: Starting threat detection with features: {...}
2025-10-22 12:00:00 - api - INFO - detect_threat:73 - 🎯 DETECTION_RESULT: {"threat_detected": true, "confidence": 0.82, "threat_types": ["ml_critical_risk"]}
2025-10-22 12:00:00 - api - INFO - detect_threat:84 - 📊 PROMETHEUS_METRIC: Incrementing THREATS_DETECTED
2025-10-22 12:00:00 - api - INFO - detect_threat:95 - 📤 RESPONSE: Sending detection result to client
```

### Scraping de Métricas
```
2025-10-22 12:00:00 - api - INFO - metrics:40 - 📥 RECEIVE: /metrics endpoint called (Prometheus scrape)
2025-10-22 12:00:00 - api - INFO - metrics:41 - 🌐 REQUEST_SOURCE: 10.244.0.1
2025-10-22 12:00:00 - metrics - INFO - generate_metrics_payload:183 - 📊 PROMETHEUS_METRICS: Generating metrics payload
2025-10-22 12:00:00 - metrics - INFO - generate_metrics_payload:194 - 📈 SINGLE_PROCESS_MODE: Using default collector
2025-10-22 12:00:00 - metrics - INFO - generate_metrics_payload:196 - ✅ SINGLE_PROCESS_PAYLOAD: Generated 2747 bytes
2025-10-22 12:00:00 - api - INFO - metrics:47 - 📤 RESPONSE: Sending metrics to Prometheus
```

## 🚀 Cómo Ver los Logs

### En Kubernetes
```bash
# Ver logs en tiempo real
kubectl logs -n ebpf-security -l app=ml-detector -f

# Ver logs recientes
kubectl logs -n ebpf-security -l app=ml-detector --tail=50

# Filtrar logs específicos
kubectl logs -n ebpf-security -l app=ml-detector | grep "PROMETHEUS_METRIC"
kubectl logs -n ebpf-security -l app=ml-detector | grep "RECEIVE"
kubectl logs -n ebpf-security -l app=ml-detector | grep "DETECTION"
```

### Para Testing Local
```bash
# Usar el script de prueba
cd applications/ml-detector/
python test_logging.py
```

## 📊 Métricas Monitoreadas

### Contadores Incrementales
- `ml_detector_requests_total` - Total de requests
- `ml_detector_threats_total` - Amenazas detectadas por tipo
- `ml_detector_processing_seconds` - Tiempo de procesamiento

### Información de Context
- **threat_type**: Tipo de amenaza detectada
- **confidence_level**: Alto/Medio/Bajo
- **source_ip**: IP origen o tipo de request

## 🎯 Beneficios

### Para Debugging
- **Tracking completo**: Desde request hasta response
- **Error analysis**: Logs detallados de fallos
- **Performance monitoring**: Tiempos de procesamiento

### Para Monitoring
- **Prometheus integration**: Visibilidad de métricas
- **Request patterns**: Análisis de tráfico
- **Threat intelligence**: Patterns de amenazas

### Para Operations
- **Kubernetes native**: Logs via `kubectl logs`
- **Structured format**: Parsing automático
- **Real-time monitoring**: Follow logs en vivo

## 🔄 Próximos Pasos

1. **Alerting**: Configurar alertas basadas en logs
2. **Log aggregation**: Centralizar logs en ELK/Loki
3. **Dashboards**: Crear dashboards de logs en Grafana
4. **Metrics correlation**: Correlacionar logs con métricas