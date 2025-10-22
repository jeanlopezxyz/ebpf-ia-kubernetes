from __future__ import annotations

import os
import logging
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client import CollectorRegistry

try:
    from prometheus_client import multiprocess
except Exception:  # pragma: no cover
    multiprocess = None  # type: ignore

# Setup logging for metrics
logger = logging.getLogger(__name__)


# Core metrics
REQUESTS_TOTAL = Counter("ml_detector_requests_total", "Total ML detector requests")

# Comprehensive threat detection metrics
THREATS_DETECTED = Counter(
    "ml_detector_threats_total", 
    "Total threats detected", 
    ["threat_type", "confidence_level", "source_ip"]
)

THREAT_CONFIDENCE = Histogram(
    "ml_detector_threat_confidence",
    "Confidence scores of detected threats",
    ["threat_type"],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

# Specific threat type metrics
PORT_SCAN_DETECTED = Counter(
    "ml_detector_port_scan_total", 
    "Port scanning attempts detected",
    ["severity", "source_ip"]
)

DDOS_DETECTED = Counter(
    "ml_detector_ddos_total",
    "DDoS attacks detected", 
    ["attack_type", "source_ip"]
)

DATA_EXFILTRATION_DETECTED = Counter(
    "ml_detector_data_exfiltration_total",
    "Data exfiltration attempts detected",
    ["direction", "source_ip"]
)

ANOMALY_DETECTED = Counter(
    "ml_detector_anomaly_total",
    "ML-based anomalies detected",
    ["model_type", "severity", "source_ip"]
)

# Model performance metrics
PROCESSING_TIME = Histogram(
    "ml_detector_processing_seconds", "Time spent processing"
)
MODEL_ACCURACY = Gauge(
    "ml_detector_model_accuracy", 
    "Current model accuracy",
    ["model_name"]
)
ANOMALY_SCORE = Gauge(
    "ml_detector_anomaly_score", 
    "Current anomaly score"
    # Removed labels to match usage in detector.py
)

# Feature analysis metrics
FEATURE_VALUES = Gauge(
    "ml_detector_feature_values",
    "Current feature values from network data",
    ["feature_name"]
)

# IP-specific metrics for Grafana dashboards
IP_PACKET_COUNT = Gauge(
    "ml_detector_ip_packet_count",
    "Packet count per source IP",
    ["source_ip"]
)

SUSPICIOUS_IP_ACTIVITY = Gauge(
    "ml_detector_suspicious_ip_activity",
    "Suspicious activity level per IP (0-1)",
    ["source_ip", "activity_type"]
)

THREAT_SEVERITY = Gauge(
    "ml_detector_threat_severity",
    "Current threat severity level (0-1)",
    ["threat_category"]
)

# Model retraining metrics
MODEL_RETRAIN_COUNT = Counter(
    "ml_detector_model_retrain_total",
    "Number of model retraining events",
    ["model_name", "trigger_reason"]
)

MODEL_RETRAIN_DURATION = Histogram(
    "ml_detector_model_retrain_seconds",
    "Time spent retraining models",
    ["model_name"]
)

# Training data quality metrics
TRAINING_DATA_QUALITY = Gauge(
    "ml_detector_training_data_quality",
    "Quality metrics for training data",
    ["metric_type"]
)

TRAINING_WINDOW_SIZE = Gauge(
    "ml_detector_training_window_size",
    "Current size of training windows",
    ["window_type"]
)

# Advanced ML model metrics (Rakuten-level)
DBSCAN_ANOMALY_SCORE = Gauge(
    "ml_detector_dbscan_anomaly_score",
    "DBSCAN-based anomaly detection score"
)

VAE_RECONSTRUCTION_ERROR = Gauge(
    "ml_detector_vae_reconstruction_error", 
    "VAE reconstruction error for sequential anomaly detection"
)

ADVANCED_MODEL_STATUS = Gauge(
    "ml_detector_advanced_model_status",
    "Status of advanced ML models (0=not ready, 1=ready)",
    ["model_name"]
)

SEQUENTIAL_ANOMALY_DETECTED = Counter(
    "ml_detector_sequential_anomaly_total",
    "Sequential anomalies detected by VAE",
    ["severity", "source_ip"] 
)

CLUSTER_ANOMALY_DETECTED = Counter(
    "ml_detector_cluster_anomaly_total", 
    "Cluster-based anomalies detected by DBSCAN",
    ["cluster_type", "source_ip"]
)

# Detection reasoning metrics for dashboard explanations
DETECTION_REASON = Counter(
    "ml_detector_detection_reason_total",
    "Detailed reasons why threats were detected",
    ["threat_type", "reason", "threshold_exceeded", "source_ip"]
)

FEATURE_THRESHOLD_VIOLATIONS = Counter(
    "ml_detector_threshold_violations_total",
    "Feature values that exceeded detection thresholds",
    ["feature_name", "threat_type", "violation_severity"]
)

MODEL_DECISION_BREAKDOWN = Gauge(
    "ml_detector_model_decision_breakdown",
    "Individual model scores for current detection",
    ["model_name", "threat_type"]
)

RULE_ENGINE_TRIGGERS = Counter(
    "ml_detector_rule_triggers_total",
    "Which rule engines triggered detections",
    ["engine_type", "rule_name", "confidence_level"]
)

# Adaptive learning metrics
LEGITIMATE_IPS_COUNT = Gauge(
    "ml_detector_legitimate_ips_total",
    "Number of IPs in the legitimate whitelist"
)

IP_CLEAN_RATIO = Gauge(
    "ml_detector_ip_clean_ratio",
    "Clean behavior ratio per IP address",
    ["source_ip"]
)

ADAPTIVE_LEARNING_STATS = Gauge(
    "ml_detector_adaptive_learning_stats",
    "Statistics about adaptive learning process",
    ["metric_type"]
)

CLEAN_DATA_RATIO = Gauge(
    "ml_detector_clean_vs_threat_ratio",
    "Ratio of clean data vs threats over time"
)

# Baseline monitoring metrics
IP_BASELINE_DEVIATIONS = Counter(
    "ml_detector_baseline_deviations_total",
    "Number of baseline deviations detected per IP",
    ["source_ip", "metric", "severity"]
)

IP_CONFIDENCE_SCORE = Gauge(
    "ml_detector_ip_confidence_score",
    "Confidence score for whitelisted IPs (0-1)",
    ["source_ip"]
)

BASELINE_Z_SCORES = Gauge(
    "ml_detector_baseline_z_scores",
    "Current Z-scores for metrics vs baseline",
    ["source_ip", "metric"]
)

WHITELISTED_IP_STATUS = Gauge(
    "ml_detector_whitelisted_ip_status",
    "Status of whitelisted IPs (1=active, 0=removed)",
    ["source_ip", "reason"]
)


def generate_metrics_payload() -> bytes:
    """Return Prometheus metrics considering multiprocess mode if enabled."""
    logger.info("📊 PROMETHEUS_METRICS: Generating metrics payload")
    
    try:
        if os.getenv("PROMETHEUS_MULTIPROC_DIR") and multiprocess is not None:
            logger.info("🔄 MULTIPROCESS_MODE: Using multiprocess collector")
            registry = CollectorRegistry()
            multiprocess.MultiProcessCollector(registry)
            payload = generate_latest(registry)
            logger.info(f"✅ MULTIPROCESS_PAYLOAD: Generated {len(payload)} bytes")
            return payload
        else:
            logger.info("📈 SINGLE_PROCESS_MODE: Using default collector")
            payload = generate_latest()
            logger.info(f"✅ SINGLE_PROCESS_PAYLOAD: Generated {len(payload)} bytes")
            
            # Log a sample of metrics for debugging
            payload_str = payload.decode('utf-8')
            ml_detector_lines = [line for line in payload_str.split('\n') if 'ml_detector' in line and not line.startswith('#')][:5]
            if ml_detector_lines:
                logger.info(f"📊 SAMPLE_METRICS: {ml_detector_lines}")
            
            return payload
    except Exception as e:
        logger.error(f"❌ METRICS_GENERATION_ERROR: {e}")
        return b"# Error generating metrics\n"

