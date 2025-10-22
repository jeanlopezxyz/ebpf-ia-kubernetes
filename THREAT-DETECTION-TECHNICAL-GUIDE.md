# 🛡️ Guía Técnica de Detección de Amenazas eBPF + AI

## 📋 Resumen Ejecutivo

Este sistema combina **eBPF** (Extended Berkeley Packet Filter) para monitoreo de red en tiempo real con **modelos de Machine Learning** para detección de amenazas avanzadas. El sistema utiliza tanto **reglas determinísticas** como **ensemble de modelos ML** para identificar amenazas con alta precisión.

## 🧠 Arquitectura de Detección

### 1. **Pipeline de Detección**
```
eBPF Monitor → Feature Extraction → Rule Engine + ML Ensemble → Threat Classification
     ↓              ↓                       ↓                        ↓
Network Data → Feature Vectors →    Confidence Scores    → Threat Response
```

### 2. **Componentes Principales**

#### **A. Reglas Determinísticas (Rule Engines)**
- **Network Rules**: Patrones conocidos de ataques de red
- **User Behavior Rules**: Comportamientos anómalos de usuario  
- **Process Monitor Rules**: Procesos maliciosos y syscalls sospechosas

#### **B. Ensemble de Modelos ML**
- **Spatial Detector (DBSCAN)**: Clustering para detección de outliers espaciales
- **Temporal Detector (VAE+LSTM)**: Secuencias temporales anómalas
- **Statistical Detector (Z-MAD)**: Desviaciones estadísticas robustas

## 🔍 Criterios de Detección Específicos

### **Amenazas de Red**

#### **1. Port Scanning (Escaneo de Puertos)**
```python
CRITERIOS:
- unique_ports > 20 puertos únicos
- packets_per_second > 100 pps
CONFIANZA: 90%
RAZÓN: "Acceso a demasiados puertos en poco tiempo indica reconocimiento"
```

#### **2. DDoS (Distributed Denial of Service)**
```python
CRITERIOS:
- packets_per_second > 1,000 pps
- bytes_per_second > 1 MB/s
CONFIANZA: 95%
RAZÓN: "Volumen de tráfico anormalmente alto desde múltiples fuentes"
```

#### **3. Data Exfiltration (Exfiltración de Datos)**
```python
CRITERIOS:
- bytes_per_second > 5 MB/s
- tcp_ratio > 90% (predominantemente TCP)
CONFIANZA: 85%
RAZÓN: "Transferencia masiva de datos TCP sugiere exfiltración"
```

#### **4. SYN Flood Attack**
```python
CRITERIOS:
- syn_packets > 500 paquetes SYN
- tcp_ratio > 95%
CONFIANZA: 92%
RAZÓN: "Exceso de paquetes SYN sin establecer conexiones completas"
```

### **Anomalías QoS (Quality of Service)**

#### **5. Latency Anomaly (Anomalía de Latencia)**
```python
CRITERIOS:
- max_latency_ms > 100ms
- avg_latency_ms > 50ms
CONFIANZA: 85%
RAZÓN: "Latencia excesiva puede indicar ataques de congestión o routing hijacking"
```

#### **6. Packet Loss Anomaly**
```python
CRITERIOS:
- packet_loss_rate > 5%
CONFIANZA: 88%
RAZÓN: "Pérdida de paquetes elevada sugiere saturación o ataques"
```

### **Anomalías de Comportamiento de Usuario**

#### **7. Brute Force Attack**
```python
CRITERIOS:
- total_attempts > 100
- failed_attempts > 50
CONFIANZA: 90%
RAZÓN: "Múltiples intentos de autenticación fallidos desde la misma fuente"
```

#### **8. Credential Stuffing**
```python
CRITERIOS:
- total_attempts > 500
- unique_source_ips > 10
CONFIANZA: 85%
RAZÓN: "Ataques distribuidos con credenciales comprometidas"
```

## 🤖 Modelos de Machine Learning

### **1. Spatial Detector (DBSCAN)**
```python
ALGORITMO: Density-Based Spatial Clustering
PARÁMETROS:
- eps = 0.5 (radio de vecindario)
- min_samples = 5 (mínimo de puntos por cluster)

FUNCIÓN: Identifica puntos de datos que no pertenecen a ningún cluster
AMENAZAS: Comportamientos únicos que no siguen patrones normales
CONFIDENCE: Basada en distancia al cluster más cercano
```

### **2. Temporal Detector (VAE + LSTM)**
```python
ALGORITMO: Variational Autoencoder con LSTM
PARÁMETROS:
- sequence_length = 10 (ventana temporal)
- latent_dim = 8 (dimensiones latentes)
- lstm_units = [32, 16]

FUNCIÓN: Reconstruye secuencias temporales normales
AMENAZAS: Secuencias que no pueden ser reconstruidas adecuadamente
CONFIDENCE: Basada en error de reconstrucción
```

### **3. Statistical Detector (Z-MAD)**
```python
ALGORITMO: Z-Score con Median Absolute Deviation
FUNCIÓN: Detecta outliers estadísticos robustos
AMENAZAS: Valores que exceden umbrales estadísticos
CONFIDENCE: Basada en desviación del comportamiento normal
```

### **Consenso de Modelos**
```python
CONSENSUS_THRESHOLDS = {
    "critical_risk": 0.8,    # ≥ 80% consenso → Riesgo Crítico
    "high_risk": 0.7,        # ≥ 70% consenso → Riesgo Alto  
    "medium_risk": 0.5,      # ≥ 50% consenso → Riesgo Medio
    "low_risk": 0.3          # ≥ 30% consenso → Riesgo Bajo
}

CLASIFICACIÓN FINAL:
- Se requiere consenso de al menos 2 modelos
- Score final = promedio de scores activos
- Clasificación basada en umbrales de consenso
```

## 📊 Métricas de Explicabilidad

### **1. Detection Reasons (Razones de Detección)**
```promql
ml_detector_detection_reason_total{
  threat_type="port_scan",
  reason="unique_ports(45)>threshold(20)",
  threshold_exceeded="unique_ports",
  source_ip="192.168.1.100"
}
```

### **2. Feature Threshold Violations**
```promql
ml_detector_threshold_violations_total{
  feature_name="bytes_per_second",
  threat_type="data_exfiltration",
  violation_severity="critical"
}
```

### **3. Model Decision Breakdown**
```promql
ml_detector_model_decision_breakdown{
  model_name="spatial",
  threat_type="ml_high_risk"
} = 0.75
```

## 🧠 Sistema de Aprendizaje Adaptativo

### **Problema Resuelto**
El sistema **NO** entrena con datos de amenazas detectadas, evitando que aprenda comportamientos maliciosos como normales.

### **Entrenamiento Inteligente**
```python
def detect(data):
    # 1. Detectar amenazas PRIMERO
    threats = detect_threats(data)
    
    if threats:
        # 🚨 AMENAZA DETECTADA - NO agregar a entrenamiento
        logger.info("🚨 THREAT_DETECTED: Not adding to training data")
        return threat_result
    else:
        # ✅ DATOS LIMPIOS - agregar a entrenamiento
        add_clean_data_to_training(data)
        logger.info("✅ CLEAN_DATA: Adding to training data")
        return clean_result
```

### **Whitelist Automática de IPs**
```python
# Auto-whitelist después de 50 observaciones limpias
if clean_ratio > 95% and observations >= 50:
    legitimate_ips.add(source_ip)
    logger.info(f"🏷️ WHITELIST: Added {ip} to legitimate IPs")

# Ejemplo: 192.168.1.50 con transferencias constantes
# Observaciones: 50 transferencias de 15MB/s
# Clean ratio: 98% (49/50 limpias)
# Resultado: IP agregada a whitelist
# Efecto: Futuras transferencias similares NO generan alertas
```

### **Blacklist Automática**
```python
# Si IP whitelisteada genera amenaza, remover inmediatamente
if threat_detected and source_ip in legitimate_ips:
    legitimate_ips.remove(source_ip)
    logger.warning(f"⚠️ BLACKLIST: Removed {ip} due to threat")
```

### **Criterios de Entrenamiento Conservadores**
```python
def is_very_normal_sample(data):
    return (
        packets_per_second < 100 and
        bytes_per_second < 1MB/s and  # Muy conservador
        unique_ports < 5
    )
```

## 🎯 Interpretación de Alertas

### **Niveles de Confianza**
- **🔴 Alta (>80%)**: Amenaza confirmada, requiere acción inmediata
- **🟡 Media (50-80%)**: Actividad sospechosa, requiere investigación
- **🟢 Baja (30-50%)**: Anomalía detectada, monitoreo continuo

### **Tipos de Detección**
- **Rule-based**: Patrones conocidos de ataques
- **ML-based**: Comportamientos anómalos detectados por IA
- **Hybrid**: Combinación de reglas y ML para mayor precisión

### **Análisis Forense**

#### **Para Port Scanning:**
1. **Verificar**: ¿Qué puertos fueron escaneados?
2. **Investigar**: ¿Es la IP conocida/legítima?
3. **Acción**: Bloquear IP si es maliciosa

#### **Para Data Exfiltration:**
1. **Verificar**: ¿Qué datos se transfirieron?
2. **Investigar**: ¿Usuario autorizado para esta transferencia?
3. **Acción**: Revisar logs de acceso a archivos sensibles

#### **Para DDoS:**
1. **Verificar**: ¿Múltiples IPs involucradas?
2. **Investigar**: ¿Patrones geográficos sospechosos?
3. **Acción**: Activar mitigación DDoS automática

## 🔧 Configuración y Tuning

### **Ajuste de Umbrales**
```python
# Archivo: constants.py
NETWORK_THRESHOLDS = {
    "port_scan": {
        "unique_ports": 20,      # Reducir para mayor sensibilidad
        "packets_per_second": 100 # Aumentar para menos falsos positivos
    }
}
```

### **Entrenamiento Continuo**
```python
TRAINING_CONFIG = {
    "interval_seconds": 30,           # Frecuencia de reentrenamiento
    "min_samples_for_training": 100,  # Mínimo de muestras
    "confidence_threshold_high": 0.8  # Umbral para datos de alta confianza
}
```

### **Ventanas de Datos**
```python
WINDOW_SIZES = {
    "high_confidence": 3000,  # Datos limpios para entrenamiento
    "all_data": 5000,         # Todos los patrones incluyendo edge cases
    "recent": 300             # Últimos 10 minutos para análisis inmediato
}
```

## 🚨 Escenarios de Respuesta

### **Amenaza Crítica Detectada**
1. **Alerta inmediata** a SOC/SIEM
2. **Registro forense** de la actividad
3. **Bloqueo automático** si está configurado
4. **Análisis de impacto** en sistemas relacionados

### **Actividad Sospechosa**
1. **Monitoreo intensificado** de la fuente
2. **Correlación** con otras alertas
3. **Notificación** a administradores
4. **Documentación** para análisis posterior

### **Falsos Positivos**
1. **Ajuste de umbrales** específicos
2. **Whitelist** para IPs/usuarios legítimos
3. **Refinamiento de modelos** ML
4. **Feedback loop** para mejora continua

---

## 📈 Métricas del Dashboard

### **Paneles Explicativos Nuevos:**

#### **"Why Threats Were Detected"**
- Muestra razones específicas de cada detección
- Incluye valores exactos que excedieron umbrales
- Identifica IP origen de cada amenaza

#### **"ML Model Decision Breakdown"**
- Scores individuales de cada modelo ML
- Consenso entre modelos para decisión final
- Transparencia en el proceso de IA

#### **"Feature Threshold Violations"**
- Qué características específicas activaron alertas
- Severidad de cada violación
- Distribución de tipos de violaciones

#### **"Rule Engine Performance"**
- Qué reglas se activaron más frecuentemente
- Rendimiento de cada motor de reglas
- Tendencias temporales de activación

Este sistema proporciona **transparencia completa** en el proceso de detección, permitiendo a los analistas de seguridad entender exactamente **por qué** se detectó una amenaza y **cómo** responder adecuadamente.