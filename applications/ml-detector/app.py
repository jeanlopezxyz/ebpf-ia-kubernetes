#!/usr/bin/env python3
"""
Main Flask application for ML Detector.

Simplified and maintainable entry point that coordinates all components.
Updated with VAE serialization fix for temporal anomaly detection.
"""
from __future__ import annotations

import logging
import os
from flask import Flask

from api import create_api
from threat_detector import ThreatDetector


def create_app() -> Flask:
    """
    Create and configure Flask application.
    
    Returns:
        Configured Flask app with all blueprints registered
    """
    app = Flask(__name__)

    # Security configuration
    app.config["MAX_CONTENT_LENGTH"] = int(
        os.getenv("MAX_CONTENT_LENGTH", str(64 * 1024))
    )

    # Enhanced logging configuration
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Console output for Kubernetes logs
        ]
    )
    
    # Set specific logger levels
    logger = logging.getLogger(__name__)
    api_logger = logging.getLogger('api')
    threat_logger = logging.getLogger('threat_detector')
    
    # Ensure our loggers are at INFO level for detailed output
    logger.setLevel(logging.INFO)
    api_logger.setLevel(logging.INFO)
    threat_logger.setLevel(logging.INFO)
    
    logger.info("🚀 ML DETECTOR: Starting up...")
    logger.info(f"📊 LOG_LEVEL: {log_level}")
    logger.info(f"🌐 MAX_CONTENT_LENGTH: {app.config['MAX_CONTENT_LENGTH']} bytes")

    # Initialize core threat detection system
    detector = ThreatDetector()
    
    # Register API blueprint
    api_bp = create_api(detector)
    app.register_blueprint(api_bp)
    
    # Health check
    @app.route('/health')
    def health():
        return {
            "status": "healthy",
            "service": "ml-detector-refactored",
            "version": "3.0.0",
            "models": {
                "spatial": detector.spatial_detector.is_trained(),
                "temporal": detector.temporal_detector.is_trained(),
                "statistical": detector.statistical_detector.is_trained()
            }
        }
    
    return app


# WSGI entrypoint for Gunicorn
app = create_app()
