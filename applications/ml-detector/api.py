from __future__ import annotations

import logging
from flask import Blueprint, jsonify, request, Response

from threat_detector import ThreatDetector
from pydantic import ValidationError
from metrics import (
    generate_metrics_payload,
    REQUESTS_TOTAL,
    PROCESSING_TIME,
    THREATS_DETECTED,
)
from schemas import DetectRequest, UserBehaviorRequest, ProcessMonitorRequest
from prom_source import PrometheusSource

logger = logging.getLogger(__name__)


def create_api(detector: ThreatDetector) -> Blueprint:
    api = Blueprint("api", __name__)

    @api.route("/health")
    def health() -> Response:
        return jsonify(
            {
                "status": "healthy",
                "service": "ml-detector",
                "version": "2.0.0",
                "models_trained": {
                    "spatial": detector.spatial_detector.is_trained(),
                    "temporal": detector.temporal_detector.is_trained(),
                    "statistical": detector.statistical_detector.is_trained()
                },
            }
        )

    @api.route("/metrics")
    def metrics() -> Response:
        logger.info(f"📥 RECEIVE: /metrics endpoint called (Prometheus scrape)")
        logger.info(f"🌐 REQUEST_SOURCE: {request.remote_addr}")
        logger.info(f"🔍 REQUEST_HEADERS: {dict(request.headers)}")
        
        payload = generate_metrics_payload()
        logger.info(f"📊 PROMETHEUS_METRICS: Generating metrics payload")
        logger.info(f"📏 PAYLOAD_SIZE: {len(payload)} bytes")
        logger.info(f"📤 RESPONSE: Sending metrics to Prometheus")
        
        return Response(payload, mimetype="text/plain; version=0.0.4; charset=utf-8")

    @api.route("/detect", methods=["POST"])
    def detect_threat() -> Response:
        if not request.is_json:
            logger.warning("❌ RECEIVE: Non-JSON request received")
            return jsonify({"error": "Unsupported Media Type, expected application/json"}), 415
        try:
            with PROCESSING_TIME.time():
                REQUESTS_TOTAL.inc()
                
                # Log incoming request details
                raw_data = request.get_json(force=True) or {}
                logger.info(f"📥 RECEIVE: /detect endpoint called")
                logger.info(f"📊 REQUEST_DATA: {raw_data}")
                logger.info(f"🔍 REQUEST_HEADERS: {dict(request.headers)}")
                logger.info(f"🌐 REQUEST_SOURCE: {request.remote_addr}")
                
                try:
                    req = DetectRequest(**raw_data)
                    logger.info(f"✅ VALIDATION: Request successfully validated")
                    logger.info(f"🔧 FEATURES: {req.to_features_dict()}")
                except ValidationError as ve:
                    logger.error(f"❌ VALIDATION_ERROR: {ve.errors()}")
                    return jsonify({"error": ve.errors()}), 400
                
                # Perform detection
                features_dict = req.to_features_dict()
                logger.info(f"🤖 DETECTION: Starting threat detection with features: {features_dict}")
                detection_result = detector.detect(features_dict)
                result = detection_result.to_dict()
                
                logger.info(f"🎯 DETECTION_RESULT: {result}")
                logger.info(f"⚠️  THREAT_DETECTED: {result.get('threat_detected', False)}")
                logger.info(f"📈 CONFIDENCE: {result.get('confidence', 0.0)}")
                logger.info(f"🏷️  THREAT_TYPES: {result.get('threat_types', [])}")
                
                # increment counters per threat (with required labels)
                for t in result.get("threat_types", []):
                    confidence = result.get("confidence", 0.0)
                    confidence_level = "high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low"
                    
                    # Log Prometheus metric update
                    logger.info(f"📊 PROMETHEUS_METRIC: Incrementing THREATS_DETECTED")
                    logger.info(f"   🏷️  threat_type={t}")
                    logger.info(f"   📊 confidence_level={confidence_level}")
                    logger.info(f"   🌐 source_ip=api_request")
                    
                    THREATS_DETECTED.labels(
                        threat_type=t, 
                        confidence_level=confidence_level,
                        source_ip="api_request"
                    ).inc()
                
                logger.info(f"📤 RESPONSE: Sending detection result to client")
                return jsonify(result)
        except Exception as e:
            logger.error(f"❌ DETECTION_ERROR: {e}")
            logger.error(f"📍 ERROR_LOCATION: /detect endpoint")
            return (
                jsonify({"error": str(e), "threat_detected": False, "confidence": 0.0}),
                500,
            )

    @api.route("/train", methods=["POST"])
    def train() -> Response:
        try:
            detector.train_models()
            return jsonify({"status": "training completed"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @api.route("/detect/user", methods=["POST"])
    def detect_user_behavior() -> Response:
        """Detect suspicious user behavior patterns."""
        if not request.is_json:
            return jsonify({"error": "Unsupported Media Type, expected application/json"}), 415
        try:
            with PROCESSING_TIME.time():
                REQUESTS_TOTAL.inc()
                try:
                    req = UserBehaviorRequest(**(request.get_json(force=True) or {}))
                except ValidationError as ve:
                    return jsonify({"error": ve.errors()}), 400
                
                detection_result = detector.detect(req.to_features_dict())
                result = detection_result.to_dict()
                
                # Update threat metrics
                for t in result.get("threat_types", []):
                    confidence = result.get("confidence", 0.0)
                    confidence_level = "high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low"
                    THREATS_DETECTED.labels(
                        threat_type=t, 
                        confidence_level=confidence_level,
                        source_ip=req.user_id
                    ).inc()
                
                return jsonify(result)
        except Exception as e:
            logger.error(f"User behavior detection error: {e}")
            return jsonify({"error": str(e), "threat_detected": False, "confidence": 0.0}), 500

    @api.route("/detect/process", methods=["POST"])
    def detect_process_behavior() -> Response:
        """Detect suspicious process behavior and malware indicators."""
        if not request.is_json:
            return jsonify({"error": "Unsupported Media Type, expected application/json"}), 415
        try:
            with PROCESSING_TIME.time():
                REQUESTS_TOTAL.inc()
                try:
                    req = ProcessMonitorRequest(**(request.get_json(force=True) or {}))
                except ValidationError as ve:
                    return jsonify({"error": ve.errors()}), 400
                
                detection_result = detector.detect(req.to_features_dict())
                result = detection_result.to_dict()
                
                # Update threat metrics
                for t in result.get("threat_types", []):
                    confidence = result.get("confidence", 0.0)
                    confidence_level = "high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low"
                    THREATS_DETECTED.labels(
                        threat_type=t, 
                        confidence_level=confidence_level,
                        source_ip=req.process_name
                    ).inc()
                
                return jsonify(result)
        except Exception as e:
            logger.error(f"Process behavior detection error: {e}")
            return jsonify({"error": str(e), "threat_detected": False, "confidence": 0.0}), 500
    
    @api.route("/stats")
    def stats() -> Response:
        return jsonify(
            {
                "models_trained": {
                    "spatial": detector.spatial_detector.is_trained(),
                    "temporal": detector.temporal_detector.is_trained(),
                    "statistical": detector.statistical_detector.is_trained()
                },
                "training_samples": len(detector.all_data_window),
                "high_confidence_samples": len(detector.high_confidence_window),
            }
        )

    @api.route("/detect/prom", methods=["POST", "GET"])
    def detect_from_prometheus() -> Response:
        """Build a feature snapshot from Prometheus and run detection.

        Optional JSON body can override query window and metric names:
        {
          "window": "1m", "metrics": {"packets": "...", "bytes": "..."}
        }
        """
        try:
            logger.info(f"📥 RECEIVE: /detect/prom endpoint called")
            logger.info(f"🌐 REQUEST_SOURCE: {request.remote_addr}")
            logger.info(f"🔧 REQUEST_METHOD: {request.method}")
            
            payload = request.get_json(silent=True) or {}
            logger.info(f"📊 REQUEST_PAYLOAD: {payload}")
            
            src = PrometheusSource()
            logger.info(f"🔗 PROMETHEUS_CONNECTION: Initializing PrometheusSource")
            
            # allow runtime override of window/metrics
            if isinstance(payload, dict):
                if "window" in payload and isinstance(payload["window"], str):
                    src.window = payload["window"]
                    logger.info(f"⏱️  WINDOW_OVERRIDE: {src.window}")
                metrics = payload.get("metrics") or {}
                if isinstance(metrics, dict):
                    src.m_packets = metrics.get("packets", src.m_packets)
                    src.m_bytes = metrics.get("bytes", src.m_bytes)
                    src.m_syn = metrics.get("syn", src.m_syn)
                    src.m_unique_ips = metrics.get("unique_ips", src.m_unique_ips)
                    src.m_unique_ports = metrics.get("unique_ports", src.m_unique_ports)
                    logger.info(f"📊 METRICS_OVERRIDE: {metrics}")
            
            logger.info(f"📡 PROMETHEUS_QUERY: Fetching features from Prometheus")
            logger.info(f"⏱️  QUERY_WINDOW: {src.window}")
            features = src.snapshot()
            logger.info(f"✅ PROMETHEUS_FEATURES: {features}")
            
            with PROCESSING_TIME.time():
                REQUESTS_TOTAL.inc()
                logger.info(f"🤖 DETECTION: Starting Prometheus-based threat detection")
                detection_result = detector.detect(features)
                result = detection_result.to_dict()
                
                logger.info(f"🎯 PROMETHEUS_DETECTION_RESULT: {result}")
                logger.info(f"⚠️  THREAT_DETECTED: {result.get('threat_detected', False)}")
                logger.info(f"📈 CONFIDENCE: {result.get('confidence', 0.0)}")
                
                # increment counters per threat (with required labels)
                for t in result.get("threat_types", []):
                    confidence = result.get("confidence", 0.0)
                    confidence_level = "high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low"
                    
                    logger.info(f"📊 PROMETHEUS_METRIC: Incrementing THREATS_DETECTED for Prometheus detection")
                    logger.info(f"   🏷️  threat_type={t}")
                    logger.info(f"   📊 confidence_level={confidence_level}")
                    logger.info(f"   🌐 source_ip=prometheus_query")
                    
                    THREATS_DETECTED.labels(
                        threat_type=t, 
                        confidence_level=confidence_level,
                        source_ip="prometheus_query"
                    ).inc()
                
                logger.info(f"📤 RESPONSE: Sending Prometheus detection result")
                return jsonify({"features": features, "result": result})
        except Exception as e:
            logger.error(f"❌ PROMETHEUS_DETECTION_ERROR: {e}")
            logger.error(f"📍 ERROR_LOCATION: /detect/prom endpoint")
            return jsonify({"error": str(e)}), 500

    @api.route("/")
    def root() -> Response:
        return jsonify(
            {
                "service": "ML Detector",
                "version": "2.0.0",
                "description": "Real-time threat detection using K-means, LOF, and One-Class SVM",
                "models": ["K-means", "Local Outlier Factor", "One-Class SVM"],
                "endpoints": {
                    "health": "/health",
                    "metrics": "/metrics", 
                    "detect": "/detect (POST)",
                    "detect_from_prom": "/detect/prom (GET|POST)",
                    "detect_user": "/detect/user (POST)",
                    "detect_process": "/detect/process (POST)",
                    "train": "/train (POST)",
                    "stats": "/stats",
                },
            }
        )

    return api
