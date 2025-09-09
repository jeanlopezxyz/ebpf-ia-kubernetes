# Security Incident Response

## Threat Detection Workflow

### 1. eBPF Event Collection
```bash
# Monitor eBPF events in real-time
kubectl logs -n ebpf-security -l app=ebpf-monitor -f

# Check network anomalies
kubectl exec -n ebpf-security deployment/ebpf-monitor -- curl localhost:8800/metrics
```

### 2. AI Threat Analysis
```bash
# Check ML detection status
kubectl logs -n ebpf-security -l app=ml-detector -f

# Manual threat analysis
curl -X POST http://ml-detector.ebpf-security:5000/detect \
  -H "Content-Type: application/json" \
  -d '{"network_data": {"src_ip": "suspicious_ip", "packets": []}}'
```

### 3. Response Actions

#### Immediate Response
1. **Isolate affected resources**
2. **Scale up monitoring** 
3. **Alert security team**
4. **Capture forensic data**

#### Investigation
1. **Review Grafana dashboards** for patterns
2. **Analyze eBPF traces** for attack vectors  
3. **Check ML model predictions** for confidence scores
4. **Correlate with threat intelligence** feeds

#### Recovery
1. **Apply network policies** to block threats
2. **Update ML models** with new threat patterns
3. **Document findings** in Backstage
4. **Update security controls** via GitOps