"""
Main ThreatDetector class - simplified and maintainable.

This is the main orchestrator that coordinates all detection models
and rule engines in a clean, maintainable way.
"""
import logging
import threading
import time
import os
from collections import deque
from typing import Dict, List, Deque, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

from models.base import DetectionResult
from models.spatial import SpatialAnomalyDetector
from models.temporal import TemporalAnomalyDetector  
from models.statistical import StatisticalAnomalyDetector
from rules.network_rules import NetworkRuleEngine
from rules.user_behavior_rules import UserBehaviorRuleEngine
from rules.process_monitor_rules import ProcessMonitorRuleEngine
from constants import (
    TRAINING_CONFIG, WINDOW_SIZES, CONSENSUS_THRESHOLDS,
    IP_SUSPICIOUS_THRESHOLD, USERNAME_TYPE_ENCODING
)
from metrics import (
    TRAINING_DATA_QUALITY, TRAINING_WINDOW_SIZE, ADVANCED_MODEL_STATUS,
    MODEL_RETRAIN_COUNT, MODEL_RETRAIN_DURATION, IP_PACKET_COUNT,
    SUSPICIOUS_IP_ACTIVITY, FEATURE_VALUES, LEGITIMATE_IPS_COUNT,
    IP_CLEAN_RATIO, ADAPTIVE_LEARNING_STATS, CLEAN_DATA_RATIO,
    IP_BASELINE_DEVIATIONS, IP_CONFIDENCE_SCORE, BASELINE_Z_SCORES,
    WHITELISTED_IP_STATUS
)

logger = logging.getLogger(__name__)


class ThreatDetector:
    """
    Main threat detection orchestrator.
    
    Coordinates multiple detection models and rule engines to provide
    comprehensive threat detection for network and authentication data.
    """
    
    def __init__(self):
        # Configuration
        self.model_path = os.getenv("MODEL_PATH", "/tmp/models")
        self.training_enabled = os.getenv("TRAINING_ENABLED", "true").lower() == "true"
        
        # Thread safety
        self._lock = threading.RLock()
        self._shutdown_event = threading.Event()
        
        # Data windows for different confidence levels
        self.high_confidence_window: Deque[np.ndarray] = deque(maxlen=WINDOW_SIZES["high_confidence"])
        self.all_data_window: Deque[np.ndarray] = deque(maxlen=WINDOW_SIZES["all_data"])
        self.recent_window: Deque[np.ndarray] = deque(maxlen=WINDOW_SIZES["recent"])
        
        # Adaptive learning - whitelist for known legitimate IPs/patterns
        self.legitimate_ips: set = set()
        self.ip_behavior_history: Dict[str, List[Dict]] = {}
        self.clean_data_count = 0
        
        # Baseline behavior monitoring for whitelisted IPs
        self.ip_baselines: Dict[str, Dict[str, float]] = {}
        self.ip_confidence_scores: Dict[str, float] = {}  # Confidence in whitelist status
        self.anomaly_threshold = 2.0  # Standard deviations for anomaly detection
        
        # Statistics
        self.high_confidence_count = 0
        self.total_samples_count = 0
        
        # Performance optimization: ThreadPool for parallel model execution
        self._executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="ml_model")
        
        # Initialize detection components
        self.spatial_detector = SpatialAnomalyDetector()
        self.temporal_detector = TemporalAnomalyDetector()
        self.statistical_detector = StatisticalAnomalyDetector()
        self.network_rules = NetworkRuleEngine()
        self.user_behavior_rules = UserBehaviorRuleEngine()
        self.process_monitor_rules = ProcessMonitorRuleEngine()
        
        # Setup
        os.makedirs(self.model_path, exist_ok=True)
        self._load_all_models()
        
        # Start background training
        if self.training_enabled:
            self._start_background_training()
    
    def extract_features(self, data: Dict[str, float], add_to_training: bool = True) -> np.ndarray:
        """Extract features and optionally add to training windows."""
        features = self._extract_features(data)
        
        if add_to_training:
            with self._lock:
                self.total_samples_count += 1
                self.all_data_window.append(features[0])
                self.recent_window.append(features[0])
                
                # High confidence determination (simplified)
                if self._is_high_confidence_sample(data):
                    self.high_confidence_window.append(features[0])
                    self.high_confidence_count += 1
        
        return features
    
    def _is_high_confidence_sample(self, data: Dict[str, float]) -> bool:
        """Determine if sample is high confidence for training."""
        # Simple heuristic: normal-looking network traffic
        pps = data.get("packets_per_second", 0)
        ports = data.get("unique_ports", 0)
        return pps < 500 and ports < 15
    
    def detect(self, data: Dict[str, float]) -> DetectionResult:
        """
        Main detection method.
        
        Args:
            data: Raw input data (network or authentication)
            
        Returns:
            DetectionResult with threat analysis
        """
        try:
            # Extract features but don't add to training yet (wait for threat assessment)
            features = self.extract_features(data, add_to_training=False)
            
            # Process IP-specific metrics
            attacking_ips = self._identify_attacking_ips(data)
            self._update_ip_metrics(data)
            
            # Check for baseline deviations in whitelisted IPs FIRST
            baseline_threats = self._detect_baseline_deviations(data)
            
            # Rule-based detection (fast) - select appropriate engine
            rule_threats = self._detect_with_rules(data)
            
            # ML-based detection (comprehensive) - but skip if IP is whitelisted AND within baseline
            source_ip = data.get("source_ip", "unknown")
            if source_ip in self.legitimate_ips and not baseline_threats:
                # IP is whitelisted and behaving normally - skip ML detection
                ml_threats = []
                logger.info(f"🏷️ WHITELIST_BYPASS: Skipping ML detection for legitimate IP {source_ip}")
            else:
                ml_threats = self._detect_with_ml_ensemble(features)
            
            # Combine results - baseline threats have HIGHEST priority
            all_threats = baseline_threats + rule_threats + ml_threats
            
            if all_threats:
                max_confidence = max(threat[1] for threat in all_threats)
                threat_types = [threat[0] for threat in all_threats]
                
                # Update metrics
                self._update_threat_metrics(threat_types, max_confidence, attacking_ips)
                
                # DO NOT add to training data - this is a detected threat
                logger.info(f"🚨 THREAT_DETECTED: Not adding to training data - {threat_types}")
                
                return DetectionResult(
                    threat_detected=True,
                    confidence=max_confidence,
                    threat_types=threat_types,
                    attacking_ips=attacking_ips,
                    detection_type=self._get_detection_type(data),
                    model_scores=self._get_model_scores()
                )
            else:
                # No threats detected - this is clean data, add to training
                self._add_clean_data_to_training(features, data)
                logger.info(f"✅ CLEAN_DATA: Adding to training data for model improvement")
            
            return DetectionResult(
                threat_detected=False,
                confidence=0.0,
                threat_types=[],
                attacking_ips=attacking_ips,
                detection_type=self._get_detection_type(data)
            )
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return DetectionResult(False, 0.0, [], [])
    
    def _extract_features(self, data: Dict[str, float]) -> np.ndarray:
        """Extract features based on data type."""
        if data.get("user_id"):
            # User behavior features
            return np.array([[
                data.get("session_duration", 0) / 3600,  # Hours
                data.get("commands_executed", 0),
                len(data.get("files_accessed", [])),
                data.get("login_time_hour", 12),
                1 if data.get("login_source") == "remote" else 0,
                data.get("privilege_escalations", 0),
                data.get("data_uploaded_mb", 0),
                data.get("sudo_commands", 0)
            ]])
        elif data.get("process_name"):
            # Process monitoring features  
            return np.array([[
                data.get("cpu_usage_percent", 0),
                data.get("memory_usage_mb", 0),
                data.get("network_connections", 0),
                data.get("files_opened", 0),
                data.get("child_processes", 0),
                1 if data.get("is_privileged") else 0,
                data.get("syscalls_per_second", 0),
                1 if data.get("is_suspicious_name") else 0,
                1 if data.get("is_suspicious_command") else 0
            ]])
        elif data.get("username_type"):
            # Authentication features
            username_type_encoded = USERNAME_TYPE_ENCODING.get(
                data.get("username_type", "username"), 0
            )
            return np.array([[
                username_type_encoded,
                data.get("total_attempts", 0),
                data.get("failed_attempts", 0),
                data.get("successful_attempts", 0),
                data.get("unique_source_ips", 0),
                data.get("privilege_level", 0)
            ]])
        else:
            # Network features
            tcp_packets = data.get("tcp_packets", 0)
            udp_packets = data.get("udp_packets", 0)
            total_packets = tcp_packets + udp_packets
            tcp_ratio = tcp_packets / total_packets if total_packets > 0 else 0.5
            
            return np.array([[
                data.get("packets_per_second", 0),
                data.get("bytes_per_second", 0),
                data.get("unique_ips", 0),
                data.get("unique_ports", 0),
                tcp_ratio,
                data.get("syn_packets", 0)
            ]])
    
    def _detect_with_ml_ensemble(self, features: np.ndarray) -> List[Tuple[str, float]]:
        """Run ML ensemble detection with consensus - OPTIMIZED for real-time."""
        scores = {}
        
        # Execute models in parallel for better real-time performance
        def run_spatial():
            if self.spatial_detector.is_trained():
                return ('spatial', self.spatial_detector.predict(features))
            return ('spatial', 0.0)
        
        def run_temporal():
            self.temporal_detector.add_sample(features)  # Still need to add sample
            if self.temporal_detector.is_trained():
                return ('temporal', self.temporal_detector.predict(features))
            return ('temporal', 0.0)
        
        def run_statistical():
            if self.statistical_detector.is_trained():
                return ('statistical', self.statistical_detector.predict(features))
            return ('statistical', 0.0)
        
        # Submit all model predictions in parallel
        futures = {
            self._executor.submit(run_spatial): 'spatial',
            self._executor.submit(run_temporal): 'temporal', 
            self._executor.submit(run_statistical): 'statistical'
        }
        
        # Collect results as they complete
        for future in as_completed(futures):
            try:
                model_name, score = future.result()
                scores[model_name] = score
            except Exception as e:
                logger.warning(f"Model {futures[future]} prediction failed: {e}")
                scores[futures[future]] = 0.0
        
        # Same consensus logic (unchanged)
        active_scores = [s for s in scores.values() if s > 0]
        
        result = []
        if len(active_scores) >= 2:  # At least 2 models agree
            final_score = np.mean(active_scores)
            
            # Classify based on consensus
            if final_score > CONSENSUS_THRESHOLDS["critical_risk"]:
                result = [("ml_critical_risk", final_score)]
            elif final_score > CONSENSUS_THRESHOLDS["high_risk"]:
                result = [("ml_high_risk", final_score)]
            elif final_score > CONSENSUS_THRESHOLDS["medium_risk"]:
                result = [("ml_medium_risk", final_score)]
            elif final_score > CONSENSUS_THRESHOLDS["low_risk"]:
                result = [("ml_low_risk", final_score)]
        
        return result
    
    def _detect_with_rules(self, data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Apply appropriate rule engine based on data type."""
        detection_type = self._get_detection_type(data)
        
        if detection_type == "network":
            return self.network_rules.detect(data)
        elif detection_type == "user_behavior":
            return self.user_behavior_rules.detect(data)
        elif detection_type == "process_monitor":
            return self.process_monitor_rules.detect(data)
        elif detection_type == "authentication":
            return self.network_rules.detect(data)  # Fallback to network rules
        else:
            return self.network_rules.detect(data)  # Default fallback
    
    def _identify_attacking_ips(self, data: Dict[str, float]) -> List[str]:
        """Identify specific attacking IPs from top_ips data."""
        top_ips = data.get("top_ips", {})
        attacking_ips = []
        
        if isinstance(top_ips, dict):
            for ip, count in top_ips.items():
                if count > IP_SUSPICIOUS_THRESHOLD:
                    attacking_ips.append(ip)
        
        return attacking_ips
    
    def _update_ip_metrics(self, data: Dict[str, float]) -> None:
        """Update IP-specific metrics for Grafana."""
        top_ips = data.get("top_ips", {})
        
        if isinstance(top_ips, dict):
            for ip, count in top_ips.items():
                IP_PACKET_COUNT.labels(source_ip=ip).set(count)
                suspicion_level = min(count / 1000.0, 1.0)
                SUSPICIOUS_IP_ACTIVITY.labels(
                    source_ip=ip, 
                    activity_type="packet_rate"
                ).set(suspicion_level)
    
    def _get_detection_type(self, data: Dict[str, float]) -> str:
        """Determine detection type based on data."""
        # Check for process monitoring data FIRST (process_name is unique identifier)
        if data.get("process_name") or data.get("process_id"):
            return "process_monitor"
        # Check for user behavior data (user_id that's not "unknown")
        elif data.get("user_id") and data.get("user_id") != "unknown":
            return "user_behavior"
        # Check for authentication data
        elif data.get("username_type"):
            return "authentication"
        # Check for QoS/transport data
        elif data.get("avg_latency_ms") is not None:
            return "transport_qos"
        else:
            return "network"
    
    def _get_model_scores(self) -> Dict[str, float]:
        """Get current model scores for debugging."""
        return {
            "spatial_trained": 1.0 if self.spatial_detector.is_trained() else 0.0,
            "temporal_trained": 1.0 if self.temporal_detector.is_trained() else 0.0,
            "statistical_trained": 1.0 if self.statistical_detector.is_trained() else 0.0
        }
    
    def _start_background_training(self) -> None:
        """Start background training thread."""
        def training_loop():
            while not self._shutdown_event.wait(TRAINING_CONFIG["interval_seconds"]):
                try:
                    self.train_models()
                except Exception as e:
                    logger.error(f"Background training error: {e}")
            logger.info("Background training stopped")
        
        thread = threading.Thread(target=training_loop, daemon=True)
        thread.start()
    
    def train_models(self) -> None:
        """Train all ML models."""
        if len(self.high_confidence_window) < TRAINING_CONFIG["min_samples_for_training"]:
            return
        
        start_time = time.time()
        
        with self._lock:
            # Prepare training data
            X_conservative = np.array(list(self.high_confidence_window))
            X_all = np.array(list(self.all_data_window)) if len(self.all_data_window) > 50 else X_conservative
            
            # Train each model
            self.spatial_detector.fit(X_all)  # DBSCAN uses all data
            self.temporal_detector.fit(X_conservative)  # VAE uses clean data
            self.statistical_detector.fit(X_all)  # ZMAD uses all history
            
            # Update metrics
            self._update_training_metrics()
        
        duration = time.time() - start_time
        MODEL_RETRAIN_DURATION.labels(model_name="ensemble").observe(duration)
        
        # Save models
        self._save_all_models()
    
    def _load_all_models(self) -> None:
        """Load all saved models."""
        self.spatial_detector.load(self.model_path)
        self.temporal_detector.load(self.model_path)
        self.statistical_detector.load(self.model_path)
    
    def _save_all_models(self) -> None:
        """Save all models."""
        self.spatial_detector.save(self.model_path)
        self.temporal_detector.save(self.model_path)
        self.statistical_detector.save(self.model_path)
    
    def _update_training_metrics(self) -> None:
        """Update Prometheus training metrics."""
        clean_ratio = self.high_confidence_count / max(self.total_samples_count, 1)
        
        TRAINING_DATA_QUALITY.labels(metric_type="clean_data_ratio").set(clean_ratio)
        TRAINING_WINDOW_SIZE.labels(window_type="high_confidence").set(len(self.high_confidence_window))
        TRAINING_WINDOW_SIZE.labels(window_type="all_data").set(len(self.all_data_window))
        
        ADVANCED_MODEL_STATUS.labels(model_name="spatial").set(1.0 if self.spatial_detector.is_trained() else 0.0)
        ADVANCED_MODEL_STATUS.labels(model_name="temporal").set(1.0 if self.temporal_detector.is_trained() else 0.0)
        ADVANCED_MODEL_STATUS.labels(model_name="statistical").set(1.0 if self.statistical_detector.is_trained() else 0.0)
        
        # Update adaptive learning metrics
        LEGITIMATE_IPS_COUNT.set(len(self.legitimate_ips))
        
        # Update IP clean ratios
        for ip, history in self.ip_behavior_history.items():
            if history:
                clean_count = sum(1 for obs in history if obs.get("clean", False))
                clean_ratio_ip = clean_count / len(history)
                IP_CLEAN_RATIO.labels(source_ip=ip).set(clean_ratio_ip)
        
        # Update adaptive learning stats
        ADAPTIVE_LEARNING_STATS.labels(metric_type="total_ips_tracked").set(len(self.ip_behavior_history))
        ADAPTIVE_LEARNING_STATS.labels(metric_type="whitelisted_ips").set(len(self.legitimate_ips))
        ADAPTIVE_LEARNING_STATS.labels(metric_type="clean_data_samples").set(self.clean_data_count)
        
        # Clean vs threat ratio
        threat_count = self.total_samples_count - self.clean_data_count
        if self.total_samples_count > 0:
            clean_vs_threat_ratio = self.clean_data_count / self.total_samples_count
            CLEAN_DATA_RATIO.set(clean_vs_threat_ratio)
        
        # Update IP confidence scores and status
        for ip in self.legitimate_ips:
            if ip in self.ip_confidence_scores:
                IP_CONFIDENCE_SCORE.labels(source_ip=ip).set(self.ip_confidence_scores[ip])
                WHITELISTED_IP_STATUS.labels(source_ip=ip, reason="active").set(1)
        
        # Mark removed IPs as inactive
        for ip in list(self.ip_confidence_scores.keys()):
            if ip not in self.legitimate_ips:
                WHITELISTED_IP_STATUS.labels(source_ip=ip, reason="removed").set(0)
    
    def _add_clean_data_to_training(self, features: np.ndarray, data: Dict[str, float]) -> None:
        """Add clean data to training windows with adaptive learning."""
        with self._lock:
            source_ip = data.get("source_ip", "unknown")
            
            # Track IP behavior history
            if source_ip != "unknown":
                if source_ip not in self.ip_behavior_history:
                    self.ip_behavior_history[source_ip] = []
                
                self.ip_behavior_history[source_ip].append({
                    "timestamp": time.time(),
                    "data": data.copy(),
                    "clean": True
                })
                
                # Keep only last 100 observations per IP
                if len(self.ip_behavior_history[source_ip]) > 100:
                    self.ip_behavior_history[source_ip] = self.ip_behavior_history[source_ip][-100:]
                
                # Auto-whitelist IPs with consistent clean behavior
                if len(self.ip_behavior_history[source_ip]) >= 50:
                    clean_count = sum(1 for obs in self.ip_behavior_history[source_ip] if obs.get("clean", False))
                    clean_ratio = clean_count / len(self.ip_behavior_history[source_ip])
                    
                    if clean_ratio > 0.95 and source_ip not in self.legitimate_ips:
                        self.legitimate_ips.add(source_ip)
                        self.ip_confidence_scores[source_ip] = clean_ratio
                        # Calculate baseline behavior for new whitelisted IP
                        self._calculate_ip_baseline(source_ip)
                        logger.info(f"🏷️ WHITELIST: Added {source_ip} to legitimate IPs (clean ratio: {clean_ratio:.2%})")
                
                # Update baseline for existing whitelisted IPs
                if source_ip in self.legitimate_ips:
                    self._update_ip_baseline(source_ip, data)
            
            # Add to training windows
            self.total_samples_count += 1
            self.clean_data_count += 1
            self.all_data_window.append(features[0])
            self.recent_window.append(features[0])
            
            # High confidence determination (more sophisticated)
            if self._is_high_confidence_sample(data) and source_ip in self.legitimate_ips:
                self.high_confidence_window.append(features[0])
                self.high_confidence_count += 1
                logger.info(f"📚 HIGH_CONFIDENCE: Added sample from whitelisted IP {source_ip}")
            elif self._is_high_confidence_sample(data):
                # Only add if it looks very normal
                if self._is_very_normal_sample(data):
                    self.high_confidence_window.append(features[0])
                    self.high_confidence_count += 1
                    logger.info(f"📚 HIGH_CONFIDENCE: Added normal sample from {source_ip}")
    
    def _is_very_normal_sample(self, data: Dict[str, float]) -> bool:
        """More strict criteria for high confidence training data."""
        pps = data.get("packets_per_second", 0)
        bps = data.get("bytes_per_second", 0)
        ports = data.get("unique_ports", 0)
        
        # Very conservative thresholds for training
        return (pps < 100 and 
                bps < 1_000_000 and  # < 1MB/s
                ports < 5)
    
    def _is_ip_whitelisted(self, source_ip: str) -> bool:
        """Check if IP is in legitimate whitelist."""
        return source_ip in self.legitimate_ips
    
    def _update_threat_metrics(self, threat_types: List[str], confidence: float, attacking_ips: List[str]) -> None:
        """Update threat-specific Prometheus metrics."""
        # Mark any IP with threats as NOT legitimate
        for ip in attacking_ips:
            if ip in self.legitimate_ips:
                self.legitimate_ips.remove(ip)
                logger.warning(f"⚠️ BLACKLIST: Removed {ip} from legitimate IPs due to threat detection")
            
            # Update IP behavior history
            if ip in self.ip_behavior_history:
                if self.ip_behavior_history[ip]:
                    self.ip_behavior_history[ip][-1]["clean"] = False
                    
            # Degrade confidence in whitelisted IPs that show threats
            if ip in self.ip_confidence_scores:
                self.ip_confidence_scores[ip] *= 0.8  # Reduce confidence by 20%
                logger.warning(f"📉 CONFIDENCE_DEGRADED: {ip} confidence reduced to {self.ip_confidence_scores[ip]:.2%}")
                
                # Remove from whitelist if confidence drops too low
                if self.ip_confidence_scores[ip] < 0.7:
                    self.legitimate_ips.remove(ip)
                    del self.ip_confidence_scores[ip]
                    if ip in self.ip_baselines:
                        del self.ip_baselines[ip]
                    logger.warning(f"🚫 WHITELIST_REMOVED: {ip} removed due to low confidence")
    
    def _detect_baseline_deviations(self, data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Detect if whitelisted IP is deviating from its established baseline behavior."""
        source_ip = data.get("source_ip", "unknown")
        threats = []
        
        if source_ip not in self.legitimate_ips or source_ip not in self.ip_baselines:
            return threats
        
        baseline = self.ip_baselines[source_ip]
        current_metrics = {
            "bytes_per_second": data.get("bytes_per_second", 0),
            "packets_per_second": data.get("packets_per_second", 0),
            "unique_ports": data.get("unique_ports", 0),
            "tcp_packets": data.get("tcp_packets", 0),
            "udp_packets": data.get("udp_packets", 0)
        }
        
        significant_deviations = []
        
        for metric, current_value in current_metrics.items():
            if metric in baseline:
                baseline_mean = baseline[metric]["mean"]
                baseline_std = baseline[metric]["std"]
                
                if baseline_std > 0:  # Avoid division by zero
                    z_score = abs(current_value - baseline_mean) / baseline_std
                    
                    if z_score > self.anomaly_threshold:
                        deviation_severity = "critical" if z_score > 4 else "high" if z_score > 3 else "medium"
                        significant_deviations.append({
                            "metric": metric,
                            "z_score": z_score,
                            "current": current_value,
                            "baseline_mean": baseline_mean,
                            "severity": deviation_severity
                        })
                        
                        # Update metrics
                        IP_BASELINE_DEVIATIONS.labels(
                            source_ip=source_ip,
                            metric=metric,
                            severity=deviation_severity
                        ).inc()
                        
                        BASELINE_Z_SCORES.labels(
                            source_ip=source_ip,
                            metric=metric
                        ).set(z_score)
                        
                        logger.warning(f"📊 BASELINE_DEVIATION: {source_ip} {metric} = {current_value:.1f} "
                                     f"(baseline: {baseline_mean:.1f}±{baseline_std:.1f}, z-score: {z_score:.2f})")
        
        # Generate threats based on significant deviations
        if significant_deviations:
            max_z_score = max(d["z_score"] for d in significant_deviations)
            confidence = min(0.95, 0.7 + (max_z_score - 2) * 0.1)  # 70-95% confidence based on z-score
            
            # Specific threat based on which metrics deviated
            bytes_deviation = any(d["metric"] == "bytes_per_second" for d in significant_deviations)
            ports_deviation = any(d["metric"] == "unique_ports" for d in significant_deviations)
            
            if bytes_deviation and any(d["current"] > d["baseline_mean"] * 3 for d in significant_deviations):
                threats.append(("baseline_data_exfiltration", confidence))
                logger.error(f"🚨 BASELINE_THREAT: {source_ip} showing unusual data transfer patterns (possible compromise)")
            elif ports_deviation:
                threats.append(("baseline_port_scanning", confidence))
                logger.error(f"🚨 BASELINE_THREAT: {source_ip} showing unusual port access patterns (possible compromise)")
            else:
                threats.append(("baseline_anomaly", confidence))
                logger.warning(f"⚠️ BASELINE_ANOMALY: {source_ip} deviating from normal behavior")
                
            # Degrade confidence in this IP
            if source_ip in self.ip_confidence_scores:
                degradation = min(0.3, max_z_score * 0.05)  # 5-30% degradation based on severity
                self.ip_confidence_scores[source_ip] *= (1 - degradation)
                logger.warning(f"📉 CONFIDENCE_DEGRADED: {source_ip} confidence reduced to {self.ip_confidence_scores[source_ip]:.2%}")
        
        return threats
    
    def _calculate_ip_baseline(self, source_ip: str) -> None:
        """Calculate baseline behavior statistics for a newly whitelisted IP."""
        if source_ip not in self.ip_behavior_history:
            return
        
        history = self.ip_behavior_history[source_ip]
        clean_observations = [obs for obs in history if obs.get("clean", False)]
        
        if len(clean_observations) < 10:
            return
        
        metrics = ["bytes_per_second", "packets_per_second", "unique_ports", "tcp_packets", "udp_packets"]
        baseline = {}
        
        for metric in metrics:
            values = [obs["data"].get(metric, 0) for obs in clean_observations if metric in obs["data"]]
            if values:
                import numpy as np
                baseline[metric] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "count": len(values)
                }
        
        self.ip_baselines[source_ip] = baseline
        logger.info(f"📊 BASELINE_CALCULATED: {source_ip} baseline established with {len(clean_observations)} observations")
        
        # Log baseline summary
        for metric, stats in baseline.items():
            logger.info(f"   {metric}: {stats['mean']:.1f}±{stats['std']:.1f} (range: {stats['min']:.1f}-{stats['max']:.1f})")
    
    def _update_ip_baseline(self, source_ip: str, data: Dict[str, float]) -> None:
        """Update baseline statistics with new clean observation (rolling average)."""
        if source_ip not in self.ip_baselines:
            return
        
        baseline = self.ip_baselines[source_ip]
        alpha = 0.1  # Learning rate for rolling average
        
        for metric in ["bytes_per_second", "packets_per_second", "unique_ports", "tcp_packets", "udp_packets"]:
            if metric in data and metric in baseline:
                current_value = data[metric]
                # Update rolling mean and std
                old_mean = baseline[metric]["mean"]
                baseline[metric]["mean"] = old_mean + alpha * (current_value - old_mean)
                # Simple std update (not perfectly accurate but computationally efficient)
                baseline[metric]["std"] = baseline[metric]["std"] * 0.95 + abs(current_value - old_mean) * 0.05
    
    def shutdown(self) -> None:
        """Gracefully shutdown background training and thread pool."""
        self._shutdown_event.set()
        self._executor.shutdown(wait=False)