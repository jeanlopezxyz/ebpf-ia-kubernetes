"""
User behavior rule-based detection.

This module contains detection logic for suspicious user activities,
insider threats, and anomalous user sessions.
"""
import logging
from typing import Dict, List, Tuple
from datetime import datetime

from models.base import BaseRuleEngine

logger = logging.getLogger(__name__)


class UserBehaviorRuleEngine(BaseRuleEngine):
    """Rule-based detection for suspicious user behavior."""
    
    def __init__(self):
        # Thresholds for user behavior anomalies
        self.thresholds = {
            "session_anomaly": {
                "max_session_hours": 12,
                "max_commands": 1000,
                "night_login_start": 23,  # 11 PM
                "night_login_end": 6      # 6 AM
            },
            "privilege_abuse": {
                "max_privilege_escalations": 5,
                "max_sudo_commands": 20,
                "suspicious_file_access": ["passwd", "shadow", "sudoers"]
            },
            "data_exfiltration_user": {
                "max_download_mb": 1000,    # 1GB download suspicious
                "max_upload_mb": 500,       # 500MB upload suspicious
                "max_files_accessed": 100
            },
            "insider_threat": {
                "off_hours_commands": 50,
                "remote_login_commands": 200,
                "failed_auth_threshold": 10
            }
        }
    
    def detect(self, data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Apply user behavior rules and return detected threats."""
        threats: List[Tuple[str, float]] = []
        
        # Session anomalies
        threats.extend(self._detect_session_anomalies(data))
        
        # Privilege abuse
        threats.extend(self._detect_privilege_abuse(data))
        
        # Data exfiltration by users
        threats.extend(self._detect_user_data_exfiltration(data))
        
        # Insider threat patterns
        threats.extend(self._detect_insider_threat(data))
        
        return threats
    
    def get_supported_data_types(self) -> List[str]:
        """Return supported data types."""
        return ["user_behavior", "authentication", "session"]
    
    def _detect_session_anomalies(self, data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Detect anomalous user sessions."""
        threats = []
        
        # Long session duration
        session_hours = data.get("session_duration", 0) / 3600
        if session_hours > self.thresholds["session_anomaly"]["max_session_hours"]:
            confidence = min(0.9, 0.5 + (session_hours / 24))
            threats.append(("long_session_anomaly", confidence))
        
        # Excessive commands
        commands = data.get("commands_executed", 0)
        if commands > self.thresholds["session_anomaly"]["max_commands"]:
            confidence = min(0.95, 0.6 + (commands / 2000))
            threats.append(("excessive_commands", confidence))
        
        # Off-hours login
        login_hour = data.get("login_time_hour", 12)
        night_start = self.thresholds["session_anomaly"]["night_login_start"]
        night_end = self.thresholds["session_anomaly"]["night_login_end"]
        
        if login_hour >= night_start or login_hour <= night_end:
            # Higher suspicion for night logins with activity
            base_confidence = 0.6
            if commands > 10:
                base_confidence += 0.2
            if data.get("privilege_escalations", 0) > 0:
                base_confidence += 0.1
            threats.append(("off_hours_activity", min(base_confidence, 0.95)))
        
        return threats
    
    def _detect_privilege_abuse(self, data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Detect privilege escalation and abuse."""
        threats = []
        
        # Multiple privilege escalations
        escalations = data.get("privilege_escalations", 0)
        if escalations > self.thresholds["privilege_abuse"]["max_privilege_escalations"]:
            confidence = min(0.9, 0.7 + (escalations / 20))
            threats.append(("privilege_escalation_abuse", confidence))
        
        # Excessive sudo usage
        sudo_commands = data.get("sudo_commands", 0)
        if sudo_commands > self.thresholds["privilege_abuse"]["max_sudo_commands"]:
            confidence = min(0.85, 0.6 + (sudo_commands / 50))
            threats.append(("excessive_sudo_usage", confidence))
        
        # Sensitive file access
        files_accessed = data.get("files_accessed", [])
        if isinstance(files_accessed, list):
            sensitive_files = [
                f for f in files_accessed 
                if any(pattern in f.lower() for pattern in self.thresholds["privilege_abuse"]["suspicious_file_access"])
            ]
            if sensitive_files:
                confidence = min(0.95, 0.8 + len(sensitive_files) * 0.05)
                threats.append(("sensitive_file_access", confidence))
        
        return threats
    
    def _detect_user_data_exfiltration(self, data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Detect data exfiltration by users."""
        threats = []
        
        # Large downloads
        download_mb = data.get("data_downloaded_mb", 0)
        if download_mb > self.thresholds["data_exfiltration_user"]["max_download_mb"]:
            confidence = min(0.9, 0.6 + (download_mb / 5000))
            threats.append(("user_large_download", confidence))
        
        # Large uploads (data exfiltration)
        upload_mb = data.get("data_uploaded_mb", 0)
        if upload_mb > self.thresholds["data_exfiltration_user"]["max_upload_mb"]:
            confidence = min(0.95, 0.7 + (upload_mb / 2000))
            threats.append(("user_data_exfiltration", confidence))
        
        # Excessive file access
        files_count = len(data.get("files_accessed", []))
        if files_count > self.thresholds["data_exfiltration_user"]["max_files_accessed"]:
            confidence = min(0.8, 0.5 + (files_count / 500))
            threats.append(("excessive_file_access", confidence))
        
        return threats
    
    def _detect_insider_threat(self, data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Detect insider threat patterns."""
        threats = []
        
        # Remote login with high activity
        if data.get("login_source") == "remote":
            commands = data.get("commands_executed", 0)
            if commands > self.thresholds["insider_threat"]["remote_login_commands"]:
                confidence = 0.75 + min(0.2, commands / 1000)
                threats.append(("insider_remote_activity", confidence))
        
        # Failed authentication attempts (reconnaissance)
        failed_attempts = data.get("failed_auth_attempts", 0)
        if failed_attempts > self.thresholds["insider_threat"]["failed_auth_threshold"]:
            confidence = min(0.85, 0.6 + (failed_attempts / 50))
            threats.append(("insider_auth_probing", confidence))
        
        # Off-hours activity combined with other factors
        login_hour = data.get("login_time_hour", 12)
        commands = data.get("commands_executed", 0)
        
        if (login_hour >= 23 or login_hour <= 6) and commands > self.thresholds["insider_threat"]["off_hours_commands"]:
            # Multiple risk factors increase confidence
            risk_factors = 0
            if data.get("privilege_escalations", 0) > 0:
                risk_factors += 1
            if data.get("data_uploaded_mb", 0) > 10:
                risk_factors += 1
            if data.get("login_source") == "remote":
                risk_factors += 1
            
            confidence = 0.65 + (risk_factors * 0.1)
            threats.append(("insider_off_hours_activity", confidence))
        
        return threats