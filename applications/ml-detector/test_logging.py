#!/usr/bin/env python3
"""
Test script to verify detailed logging is working correctly.
"""
import json
import requests
import time

def test_ml_detector_logging():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing ML Detector detailed logging...")
    
    # Test 1: Health endpoint
    print("\n1️⃣ Testing /health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health status: {response.status_code}")
    except Exception as e:
        print(f"❌ Health test failed: {e}")
    
    # Test 2: Metrics endpoint  
    print("\n2️⃣ Testing /metrics endpoint...")
    try:
        response = requests.get(f"{base_url}/metrics")
        print(f"✅ Metrics status: {response.status_code}")
        print(f"📊 Metrics size: {len(response.text)} bytes")
    except Exception as e:
        print(f"❌ Metrics test failed: {e}")
    
    # Test 3: Detection endpoint
    print("\n3️⃣ Testing /detect endpoint...")
    test_data = {
        "packets": 1000,
        "bytes": 50000,
        "syn_packets": 100,
        "unique_ips": 10,
        "unique_ports": 5,
        "duration": 60
    }
    
    try:
        response = requests.post(
            f"{base_url}/detect",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Detection status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"🎯 Threat detected: {result.get('threat_detected', False)}")
            print(f"📈 Confidence: {result.get('confidence', 0.0)}")
    except Exception as e:
        print(f"❌ Detection test failed: {e}")
    
    # Test 4: Prometheus detection endpoint
    print("\n4️⃣ Testing /detect/prom endpoint...")
    try:
        response = requests.get(f"{base_url}/detect/prom")
        print(f"✅ Prometheus detection status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"🔗 Features from Prometheus: {result.get('features', {})}")
    except Exception as e:
        print(f"❌ Prometheus detection test failed: {e}")
    
    print("\n🎉 Logging tests completed!")
    print("📋 Check the application logs for detailed output with emojis and structured information.")

if __name__ == "__main__":
    test_ml_detector_logging()