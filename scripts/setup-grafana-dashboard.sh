#!/bin/bash

# Script para configurar dashboard de eBPF + AI en Grafana
# Configuración
GRAFANA_URL="http://localhost:3001"
GRAFANA_USER="admin"
GRAFANA_PASSWORD="admin123"
PROMETHEUS_URL="http://prometheus-server.prometheus.svc.cluster.local:80"

echo "🚀 Configurando Grafana Dashboard para eBPF + AI Security Monitoring..."

# Función para hacer peticiones a Grafana API
grafana_api() {
    curl -s -u "$GRAFANA_USER:$GRAFANA_PASSWORD" \
         -H "Content-Type: application/json" \
         "$GRAFANA_URL$1" \
         "${@:2}"
}

# 1. Verificar conexión a Grafana
echo "📡 Verificando conexión a Grafana..."
if ! grafana_api "/api/health" > /dev/null 2>&1; then
    echo "❌ No se puede conectar a Grafana en $GRAFANA_URL"
    echo "💡 Asegúrate de que el port-forward esté activo:"
    echo "   kubectl port-forward -n grafana svc/grafana 3000:3000"
    exit 1
fi
echo "✅ Conexión a Grafana exitosa"

# 2. Verificar si ya existe el data source de Prometheus
echo "🔍 Verificando data source de Prometheus..."
DATASOURCE_EXISTS=$(grafana_api "/api/datasources/name/prometheus" | jq -r '.name // empty' 2>/dev/null)

if [ -z "$DATASOURCE_EXISTS" ]; then
    echo "📊 Creando data source de Prometheus..."
    grafana_api "/api/datasources" -X POST -d '{
        "name": "prometheus",
        "type": "prometheus",
        "url": "'"$PROMETHEUS_URL"'",
        "access": "proxy",
        "isDefault": true
    }'
    echo "✅ Data source de Prometheus creado"
else
    echo "✅ Data source de Prometheus ya existe"
fi

# 3. Importar dashboard
echo "📈 Importando dashboard de eBPF + AI Security..."
DASHBOARD_JSON=$(cat ../dashboards/ebpf-ai-security-dashboard.json)

grafana_api "/api/dashboards/db" -X POST -d '{
    "dashboard": '"$(echo "$DASHBOARD_JSON" | jq '.dashboard')"',
    "overwrite": true
}'

if [ $? -eq 0 ]; then
    echo "✅ Dashboard importado exitosamente"
    echo ""
    echo "🎯 Dashboard configurado con las siguientes métricas:"
    echo "   🚨 Amenazas detectadas en tiempo real"
    echo "   📊 Tasa de peticiones al ML Detector"
    echo "   🌐 Tráfico de red eBPF"
    echo "   ⚡ Eventos eBPF procesados"
    echo "   🔍 Timeline de detección de amenazas"
    echo "   📈 Performance del procesamiento ML"
    echo "   🎯 Scores de anomalías ML"
    echo "   🔄 Estado de comunicación"
    echo ""
    echo "🌐 Accede al dashboard en: $GRAFANA_URL"
    echo "👤 Usuario: $GRAFANA_USER"
    echo "🔑 Password: $GRAFANA_PASSWORD"
else
    echo "❌ Error importando dashboard"
    exit 1
fi