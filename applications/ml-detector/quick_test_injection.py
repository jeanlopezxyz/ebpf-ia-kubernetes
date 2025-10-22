#!/usr/bin/env python3
"""
🚀 Quick Test Injection - Prueba inmediata de detección

Script para probar rápidamente si el sistema detecta amenazas específicas.
Inyecta datos directamente al ML Detector vía POST request.
"""
import requests
import json
import time
from datetime import datetime

# Configuración
ML_DETECTOR_URL = "http://localhost:5000"  # Cambiar según tu deployment
# Para Kubernetes: "http://ml-detector-service.ebpf-security.svc.cluster.local:5000"

def test_detection(test_name: str, data: dict, should_detect: bool = True):
    """Prueba un escenario específico y valida si se detecta."""
    print(f"\n🎯 TESTING: {test_name}")
    print(f"📊 Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(
            f"{ML_DETECTOR_URL}/detect",
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            threat_detected = result.get("threat_detected", False)
            confidence = result.get("confidence", 0.0)
            threat_types = result.get("threat_types", [])
            
            if threat_detected:
                print(f"✅ DETECTADO: {threat_types} (Confianza: {confidence:.2%})")
                if should_detect:
                    print(f"🎉 CORRECTO: Era esperado que se detectara")
                else:
                    print(f"⚠️ FALSO POSITIVO: No debería haberse detectado")
            else:
                print(f"❌ NO DETECTADO")
                if should_detect:
                    print(f"🚨 FALSO NEGATIVO: Debería haberse detectado")
                else:
                    print(f"✅ CORRECTO: No era amenaza")
                    
            return result
        else:
            print(f"❌ ERROR HTTP: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def main():
    print("🚨 QUICK VULNERABILITY DETECTION TESTS")
    print("=" * 50)
    
    # TEST 1: Data Exfiltration (DEBE detectarse - umbral: 3MB/s)
    test_detection(
        "Data Exfiltration (5MB/s)",
        {
            "source_ip": "192.168.1.100",
            "packets_per_second": 1200,
            "bytes_per_second": 5_000_000,  # 5MB/s - Por encima del umbral de 3MB/s
            "unique_ports": 8,
            "tcp_packets": 1100,  # TCP ratio = 91.7% > 85%
            "udp_packets": 100,
            "syn_packets": 25,
            "timestamp": datetime.now().isoformat()
        },
        should_detect=True
    )
    
    time.sleep(2)
    
    # TEST 2: Port Scanning (DEBE detectarse - umbral: 15 puertos y 80 pps)
    test_detection(
        "Port Scanning (20 puertos, 120 pps)",
        {
            "source_ip": "10.0.0.100",
            "packets_per_second": 120,  # > 80 pps
            "bytes_per_second": 800_000,
            "unique_ports": 20,  # > 15 puertos
            "tcp_packets": 110,
            "udp_packets": 10,
            "syn_packets": 60,
            "timestamp": datetime.now().isoformat()
        },
        should_detect=True
    )
    
    time.sleep(2)
    
    # TEST 3: Brute Force Attack (DEBE detectarse - umbral: 15 failed attempts)
    test_detection(
        "Brute Force Attack (20 failed attempts)",
        {
            "source_ip": "203.0.113.45",
            "username_type": "username", 
            "total_attempts": 25,
            "failed_attempts": 20,  # > 15 umbral
            "successful_attempts": 5,
            "unique_source_ips": 1,
            "privilege_level": 0,
            "timestamp": datetime.now().isoformat()
        },
        should_detect=True
    )
    
    time.sleep(2)
    
    # TEST 4: Tráfico Normal (NO debe detectarse)
    test_detection(
        "Tráfico Normal",
        {
            "source_ip": "192.168.1.50",
            "packets_per_second": 25,
            "bytes_per_second": 500_000,  # 500KB/s - normal
            "unique_ports": 3,
            "tcp_packets": 20,
            "udp_packets": 5,
            "syn_packets": 3,
            "timestamp": datetime.now().isoformat()
        },
        should_detect=False
    )
    
    time.sleep(2)
    
    # TEST 5: Usuario Sospechoso (DEBE detectarse - umbral: 4 privilege escalations)
    test_detection(
        "Usuario Sospechoso (6 privilege escalations)",
        {
            "source_ip": "192.168.1.75",
            "user_id": "admin",
            "session_duration": 3600,  # 1 hora
            "commands_executed": 80,
            "files_accessed": ["/etc/passwd", "/etc/shadow"],  # Archivos sensibles
            "login_time_hour": 3,  # 3 AM - fuera de horario
            "login_source": "remote",
            "privilege_escalations": 6,  # > 4 umbral
            "data_uploaded_mb": 100,
            "sudo_commands": 6,
            "timestamp": datetime.now().isoformat()
        },
        should_detect=True
    )
    
    time.sleep(2)
    
    # TEST 6: Proceso Malicioso (DEBE detectarse)
    test_detection(
        "Proceso Malicioso",
        {
            "source_ip": "192.168.1.80",
            "process_name": "mimikatz.exe",  # Herramienta conocida de hacking
            "cpu_usage_percent": 85,
            "memory_usage_mb": 250,
            "network_connections": 15,
            "files_opened": 75,  # MUCHOS archivos
            "child_processes": 8,
            "is_privileged": True,
            "syscalls_per_second": 500,  # MUCHAS syscalls
            "is_suspicious_name": True,
            "is_suspicious_command": True,
            "timestamp": datetime.now().isoformat()
        },
        should_detect=True
    )
    
    time.sleep(2)
    
    # TEST 7: ESCENARIO CRÍTICO - IP Whitelisted Comprometida
    print("\n🔥 ESCENARIO CRÍTICO: IP Whitelisted Comprometida")
    
    # Primero establecer comportamiento normal
    for i in range(5):
        print(f"📊 Estableciendo baseline normal {i+1}/5...")
        test_detection(
            f"Baseline Normal {i+1}",
            {
                "source_ip": "192.168.1.50",  # IP que será whitelisted
                "packets_per_second": 15,
                "bytes_per_second": 800_000,  # 800KB/s normal
                "unique_ports": 2,
                "tcp_packets": 12,
                "udp_packets": 3,
                "syn_packets": 2,
                "timestamp": datetime.now().isoformat()
            },
            should_detect=False
        )
        time.sleep(1)
    
    print("⏳ Esperando que IP sea whitelisted...")
    time.sleep(10)
    
    # Ahora simular compromiso con comportamiento muy diferente al baseline
    test_detection(
        "IP WHITELISTED COMPROMETIDA - Baseline Deviation",
        {
            "source_ip": "192.168.1.50",  # MISMA IP, pero comportamiento diferente
            "packets_per_second": 300,  # 20x más que normal (15 → 300)
            "bytes_per_second": 20_000_000,  # 25x más que normal (800KB → 20MB/s)
            "unique_ports": 25,  # 12x más que normal (2 → 25)
            "tcp_packets": 280,
            "udp_packets": 20,
            "syn_packets": 15,
            "timestamp": datetime.now().isoformat()
        },
        should_detect=True  # DEBE detectar baseline deviation
    )
    
    print("\n" + "=" * 50)
    print("🏁 TESTS COMPLETADOS")
    print("📋 Revisa dashboard de Grafana para ver las detecciones")
    print("🔍 Busca métricas como:")
    print("   - ml_detector_threats_total")
    print("   - ml_detector_detection_reason_total") 
    print("   - ml_detector_baseline_deviations_total")

if __name__ == "__main__":
    main()