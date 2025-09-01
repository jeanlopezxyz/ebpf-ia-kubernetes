"""
Process monitoring rule-based detection.

This module contains detection logic for suspicious processes,
malware behavior, and anomalous system activities.
"""
import logging
from typing import Dict, List, Tuple

from models.base import BaseRuleEngine

logger = logging.getLogger(__name__)


class ProcessMonitorRuleEngine(BaseRuleEngine):
    """Rule-based detection for suspicious process behavior."""
    
    def __init__(self):
        # Thresholds for process anomalies
        self.thresholds = {
            "resource_abuse": {
                "max_cpu_percent": 90,
                "max_memory_mb": 4096,
                "max_network_connections": 100,
                "max_files_opened": 500
            },
            "malware_behavior": {
                "max_child_processes": 10,
                "max_syscalls_per_second": 1000,
                "suspicious_execution_time": 300,  # 5 minutes
                "network_threshold_mb": 100
            },
            "privilege_escalation": {
                "unprivileged_high_cpu": 80,    # High CPU without privileges
                "privileged_network_mb": 50,     # Privileged process with network
                "privileged_file_access": 200   # Many files for privileged process
            },
            "persistence_mechanism": {
                "long_execution_hours": 24,
                "background_network_mb": 10,
                "background_syscalls": 100
            }
        }
        
        # Known suspicious process patterns
        self.suspicious_process_names = [
            'nc', 'netcat', 'socat', 'telnet', 'nmap', 'masscan',
            'metasploit', 'msfconsole', 'msfvenom', 
            'python -c', 'perl -e', 'ruby -e', 'node -e',
            'base64', 'xxd', 'hexdump', 'strings',
            'wget', 'curl', 'aria2c', 'axel'
        ]
        
        # Suspicious parent processes (process injection indicators)
        self.suspicious_parents = [
            'explorer.exe', 'winlogon.exe', 'csrss.exe',
            'svchost.exe', 'lsass.exe', 'systemd'
        ]
    
    def detect(self, data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Apply process monitoring rules and return detected threats."""
        threats: List[Tuple[str, float]] = []
        
        # Resource abuse detection
        threats.extend(self._detect_resource_abuse(data))
        
        # Malware behavioral patterns
        threats.extend(self._detect_malware_behavior(data))
        
        # Privilege escalation attempts
        threats.extend(self._detect_privilege_escalation(data))
        
        # Persistence mechanisms
        threats.extend(self._detect_persistence(data))
        
        # Process name and command line analysis
        threats.extend(self._detect_suspicious_processes(data))
        
        return threats
    
    def get_supported_data_types(self) -> List[str]:
        """Return supported data types."""
        return ["process_monitor", "system_behavior", "malware"]
    
    def _detect_resource_abuse(self, data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Detect processes abusing system resources."""
        threats = []
        
        # CPU abuse
        cpu_usage = data.get("cpu_usage_percent", 0)
        if cpu_usage > self.thresholds["resource_abuse"]["max_cpu_percent"]:
            confidence = min(0.9, 0.6 + (cpu_usage / 100))
            threats.append(("cpu_resource_abuse", confidence))
        
        # Memory abuse
        memory_mb = data.get("memory_usage_mb", 0)
        if memory_mb > self.thresholds["resource_abuse"]["max_memory_mb"]:
            confidence = min(0.85, 0.5 + (memory_mb / 8192))
            threats.append(("memory_resource_abuse", confidence))
        
        # Network connection abuse
        connections = data.get("network_connections", 0)
        if connections > self.thresholds["resource_abuse"]["max_network_connections"]:
            confidence = min(0.9, 0.7 + (connections / 500))
            threats.append(("network_connection_abuse", confidence))
        
        # File handle abuse
        files_opened = data.get("files_opened", 0)
        if files_opened > self.thresholds["resource_abuse"]["max_files_opened"]:
            confidence = min(0.8, 0.6 + (files_opened / 1000))
            threats.append(("file_handle_abuse", confidence))
        
        return threats
    
    def _detect_malware_behavior(self, data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Detect malware-like process behavior."""
        threats = []
        
        # Process spawning behavior
        child_processes = data.get("child_processes", 0)
        if child_processes > self.thresholds["malware_behavior"]["max_child_processes"]:
            confidence = min(0.95, 0.8 + (child_processes / 50))
            threats.append(("process_spawning_anomaly", confidence))
        
        # High syscall rate (injection, hooking)
        syscalls = data.get("syscalls_per_second", 0)
        if syscalls > self.thresholds["malware_behavior"]["max_syscalls_per_second"]:
            confidence = min(0.9, 0.7 + (syscalls / 5000))
            threats.append(("high_syscall_activity", confidence))
        
        # Network activity from unexpected process
        network_sent = data.get("network_bytes_sent", 0) / 1024 / 1024  # MB
        network_recv = data.get("network_bytes_received", 0) / 1024 / 1024  # MB
        total_network = network_sent + network_recv
        
        if total_network > self.thresholds["malware_behavior"]["network_threshold_mb"]:
            # Check if this is expected to have network activity
            process_name = data.get("process_name", "").lower()
            expected_network_processes = ['chrome', 'firefox', 'curl', 'wget', 'ssh', 'scp']
            
            if not any(proc in process_name for proc in expected_network_processes):
                confidence = min(0.85, 0.6 + (total_network / 500))
                threats.append(("unexpected_network_activity", confidence))
        
        return threats
    
    def _detect_privilege_escalation(self, data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Detect privilege escalation attempts."""
        threats = []
        
        is_privileged = data.get("is_privileged", False)
        cpu_usage = data.get("cpu_usage_percent", 0)
        network_mb = (data.get("network_bytes_sent", 0) + data.get("network_bytes_received", 0)) / 1024 / 1024
        files_opened = data.get("files_opened", 0)
        
        # Unprivileged process with high CPU (possible exploit)
        if not is_privileged and cpu_usage > self.thresholds["privilege_escalation"]["unprivileged_high_cpu"]:
            confidence = 0.75 + min(0.2, (cpu_usage - 80) / 100)
            threats.append(("unprivileged_high_cpu", confidence))
        
        # Privileged process with unexpected network activity
        if is_privileged and network_mb > self.thresholds["privilege_escalation"]["privileged_network_mb"]:
            confidence = 0.8 + min(0.15, network_mb / 200)
            threats.append(("privileged_network_activity", confidence))
        
        # Privileged process accessing many files (data harvesting)
        if is_privileged and files_opened > self.thresholds["privilege_escalation"]["privileged_file_access"]:
            confidence = 0.7 + min(0.25, files_opened / 1000)
            threats.append(("privileged_file_harvesting", confidence))
        
        return threats
    
    def _detect_persistence(self, data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Detect persistence mechanisms."""
        threats = []
        
        # Long-running background processes with network activity
        execution_hours = data.get("execution_time_seconds", 0) / 3600
        network_mb = (data.get("network_bytes_sent", 0) + data.get("network_bytes_received", 0)) / 1024 / 1024
        syscalls = data.get("syscalls_per_second", 0)
        
        if execution_hours > self.thresholds["persistence_mechanism"]["long_execution_hours"]:
            risk_factors = 0
            
            # Background network activity
            if network_mb > self.thresholds["persistence_mechanism"]["background_network_mb"]:
                risk_factors += 1
            
            # Background syscall activity
            if syscalls > self.thresholds["persistence_mechanism"]["background_syscalls"]:
                risk_factors += 1
            
            # Suspicious process name
            if data.get("is_suspicious_name", False):
                risk_factors += 1
            
            if risk_factors >= 2:
                confidence = 0.7 + (risk_factors * 0.1)
                threats.append(("persistence_mechanism", min(confidence, 0.95)))
        
        return threats
    
    def _detect_suspicious_processes(self, data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Detect processes with suspicious names or command lines."""
        threats = []
        
        # Suspicious process name
        if data.get("is_suspicious_name", False):
            confidence = 0.8
            # Increase confidence based on other factors
            if data.get("is_privileged", False):
                confidence += 0.1
            if data.get("network_connections", 0) > 5:
                confidence += 0.05
            
            threats.append(("suspicious_process_name", min(confidence, 0.95)))
        
        # Suspicious command line
        if data.get("is_suspicious_command", False):
            confidence = 0.85
            # Command injection or shell commands are highly suspicious
            command_line = data.get("command_line", "").lower()
            if any(pattern in command_line for pattern in ['reverse shell', 'nc -l', '/etc/passwd']):
                confidence = 0.95
            
            threats.append(("suspicious_command_execution", confidence))
        
        # Process injection indicators (suspicious parent)
        parent = data.get("parent_process", "").lower()
        if any(susp_parent in parent for susp_parent in self.suspicious_parents):
            process_name = data.get("process_name", "")
            # Legitimate child processes of system processes
            if not any(legit in process_name.lower() for legit in ['system', 'service', 'daemon']):
                threats.append(("process_injection_indicator", 0.8))
        
        return threats