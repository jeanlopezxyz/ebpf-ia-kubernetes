"""
Immediate Threat Detection Engine.

This module provides zero-day protection without requiring ML training.
Detects known attack patterns, suspicious IPs, and user intrusions immediately.
"""
import logging
import re
from typing import Dict, List, Tuple
from datetime import datetime, time

from models.base import BaseRuleEngine
from constants import IMMEDIATE_THREAT_THRESHOLDS, MALICIOUS_PATTERNS

logger = logging.getLogger(__name__)


class ImmediateThreatEngine(BaseRuleEngine):
    """Immediate threat detection without ML training dependency."""
    
    def __init__(self):
        self.known_good_ips = set()  # Empty initially - will learn over time
        self.business_hours = (time(8, 0), time(18, 0))  # 8 AM - 6 PM
        
    def detect(self, data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Detect immediate threats without ML training."""
        threats: List[Tuple[str, float]] = []
        
        source_ip = data.get("source_ip", "unknown")
        
        # IMMEDIATE PROTECTION: Unknown IP analysis
        if source_ip not in self.known_good_ips:
            threats.extend(self._detect_unknown_ip_threats(data))
        
        # User intrusion detection
        threats.extend(self._detect_user_intrusions(data))
        
        # Malicious pattern detection
        threats.extend(self._detect_malicious_patterns(data))
        
        # Off-hours access detection
        threats.extend(self._detect_off_hours_access(data))
        
        return threats
    
    def get_supported_data_types(self) -> List[str]:
        """Return supported data types."""
        return ["network", "user_behavior", "process_monitor", "authentication"]
    
    def _detect_unknown_ip_threats(self, data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Detect threats from unknown/untrusted IPs."""
        threats = []
        source_ip = data.get("source_ip", "unknown")
        
        if source_ip in self.known_good_ips:
            return threats  # Skip for known good IPs
        
        # High-volume data transfer from unknown IP
        bps = data.get("bytes_per_second", 0)
        if bps > IMMEDIATE_THREAT_THRESHOLDS["unknown_ip_data_exfiltration"]["bytes_per_second"]:
            confidence = IMMEDIATE_THREAT_THRESHOLDS["unknown_ip_data_exfiltration"]["confidence"]
            threats.append(("unknown_ip_data_exfiltration", confidence))
            logger.warning(f"🚨 IMMEDIATE_THREAT: Unknown IP {source_ip} transferring {bps/1_000_000:.1f}MB/s")
        
        # Port scanning from unknown IP  
        ports = data.get("unique_ports", 0)
        pps = data.get("packets_per_second", 0)
        port_threshold = IMMEDIATE_THREAT_THRESHOLDS["unknown_ip_port_scan"]["unique_ports"]
        pps_threshold = IMMEDIATE_THREAT_THRESHOLDS["unknown_ip_port_scan"]["packets_per_second"]
        
        if ports > port_threshold and pps > pps_threshold:
            confidence = IMMEDIATE_THREAT_THRESHOLDS["unknown_ip_port_scan"]["confidence"]
            threats.append(("unknown_ip_port_scan", confidence))
            logger.warning(f"🚨 IMMEDIATE_THREAT: Unknown IP {source_ip} scanning {ports} ports at {pps} pps")
        
        # DDoS from unknown IP
        ddos_pps = IMMEDIATE_THREAT_THRESHOLDS["unknown_ip_ddos"]["packets_per_second"]
        ddos_bps = IMMEDIATE_THREAT_THRESHOLDS["unknown_ip_ddos"]["bytes_per_second"]
        
        if pps > ddos_pps and bps > ddos_bps:
            confidence = IMMEDIATE_THREAT_THRESHOLDS["unknown_ip_ddos"]["confidence"]
            threats.append(("unknown_ip_ddos", confidence))
            logger.error(f"🚨 IMMEDIATE_THREAT: Unknown IP {source_ip} DDoS attack - {pps} pps, {bps/1_000_000:.1f}MB/s")
        
        return threats
    
    def _detect_user_intrusions(self, data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Detect suspicious user behavior indicating intrusion."""
        threats = []
        
        # Excessive failed logins
        failed_logins = data.get("failed_attempts", 0)
        if failed_logins > IMMEDIATE_THREAT_THRESHOLDS["suspicious_user_activity"]["failed_logins"]:
            confidence = IMMEDIATE_THREAT_THRESHOLDS["suspicious_user_activity"]["confidence"]
            threats.append(("brute_force_intrusion", confidence))
            logger.warning(f"🚨 USER_INTRUSION: {failed_logins} failed login attempts detected")
        
        # Excessive privilege escalations
        privilege_esc = data.get("privilege_escalations", 0)
        if privilege_esc > IMMEDIATE_THREAT_THRESHOLDS["suspicious_user_activity"]["privilege_escalations"]:
            confidence = IMMEDIATE_THREAT_THRESHOLDS["suspicious_user_activity"]["confidence"]
            threats.append(("privilege_escalation_attack", confidence))
            logger.warning(f"🚨 USER_INTRUSION: {privilege_esc} privilege escalation attempts")
        
        # New user creation (highly suspicious)
        if data.get("new_user_created", False):
            confidence = IMMEDIATE_THREAT_THRESHOLDS["intrusion_indicators"]["confidence"]
            threats.append(("unauthorized_user_creation", confidence))
            logger.error(f"🚨 USER_INTRUSION: Unauthorized user creation detected")
        
        # Suspicious user commands
        user_id = data.get("user_id", "unknown")
        commands = data.get("commands_executed", 0)
        files_accessed = data.get("files_accessed", [])
        
        if commands > 100:  # Excessive command execution
            threats.append(("suspicious_user_activity", 0.75))
            logger.warning(f"🚨 USER_INTRUSION: User {user_id} executed {commands} commands")
        
        # Access to sensitive files
        sensitive_patterns = ["/etc/passwd", "/etc/shadow", "ssh_config", "authorized_keys"]
        if isinstance(files_accessed, list):
            for file_path in files_accessed:
                if any(pattern in str(file_path).lower() for pattern in sensitive_patterns):
                    threats.append(("sensitive_file_access", 0.85))
                    logger.error(f"🚨 USER_INTRUSION: Access to sensitive file {file_path}")
        
        return threats
    
    def _detect_malicious_patterns(self, data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Detect known malicious patterns in processes and commands."""
        threats = []
        
        # Check process names for known malicious tools
        process_name = data.get("process_name", "")
        if process_name:
            for malicious_process in MALICIOUS_PATTERNS["suspicious_processes"]:
                if malicious_process.lower() in process_name.lower():
                    threats.append(("malicious_process_detected", 0.95))
                    logger.error(f"🚨 MALICIOUS_PROCESS: {malicious_process} detected in {process_name}")
        
        # Check command patterns
        command = data.get("command", "")
        if command:
            for signature in MALICIOUS_PATTERNS["known_attack_signatures"]:
                if re.search(signature["pattern"], command, re.IGNORECASE):
                    threat_type = f"malicious_command_{signature['type']}"
                    threats.append((threat_type, 0.90))
                    logger.error(f"🚨 MALICIOUS_COMMAND: {signature['type']} pattern detected")
        
        # Check for suspicious file types
        files_opened = data.get("files_opened", 0)
        if files_opened > 50:  # Opening many files quickly
            threats.append(("file_enumeration_attack", 0.80))
            logger.warning(f"🚨 FILE_ENUMERATION: {files_opened} files accessed rapidly")
        
        return threats
    
    def _detect_off_hours_access(self, data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Detect access during off-business hours."""
        threats = []
        
        # Check if current time is outside business hours
        current_time = datetime.now().time()
        start_time, end_time = self.business_hours
        
        if not (start_time <= current_time <= end_time):
            # Off-hours access detected
            login_attempts = data.get("total_attempts", 0)
            if login_attempts > 0:
                threats.append(("off_hours_access", 0.70))
                logger.warning(f"🚨 OFF_HOURS_ACCESS: Login attempts at {current_time}")
        
        return threats
    
    def add_known_good_ip(self, ip: str) -> None:
        """Add IP to known good list (called when IP becomes whitelisted)."""
        self.known_good_ips.add(ip)
        logger.info(f"✅ KNOWN_GOOD_IP: Added {ip} to immediate protection whitelist")
    
    def remove_known_good_ip(self, ip: str) -> None:
        """Remove IP from known good list (called when IP is blacklisted)."""
        if ip in self.known_good_ips:
            self.known_good_ips.remove(ip)
            logger.warning(f"❌ KNOWN_GOOD_IP: Removed {ip} from immediate protection whitelist")