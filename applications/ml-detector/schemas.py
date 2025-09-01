from __future__ import annotations

from pydantic import BaseModel, confloat, conint
from typing import List, Optional


class DetectRequest(BaseModel):
    # Network traffic features (original)
    packets_per_second: confloat(ge=0) = 0
    bytes_per_second: confloat(ge=0) = 0
    unique_ips: conint(ge=0) = 0
    unique_ports: conint(ge=0) = 0
    tcp_packets: conint(ge=0) = 0
    udp_packets: conint(ge=0) = 0 
    syn_packets: conint(ge=0) = 0
    
    # Authentication/Security logs features (Rakuten-style)
    username_type: str = None                    # "service", "password", "command", "username"
    confidence_score: confloat(ge=0, le=1) = None
    privilege_level: conint(ge=0, le=1) = None   # 0=normal, 1=elevated
    total_attempts: conint(ge=0) = None
    failed_attempts: conint(ge=0) = None  
    successful_attempts: conint(ge=0) = None
    unique_source_ips: conint(ge=0) = None
    
    # For backward compatibility - deprecated
    tcp_ratio: confloat(ge=0, le=1) = None

    def to_features_dict(self) -> dict:
        data = self.dict()
        # Remove None values for backward compatibility
        return {k: v for k, v in data.items() if v is not None}
    
    def get_detection_type(self) -> str:
        """Determine detection type based on available data."""
        if self.username_type is not None:
            return "authentication"
        else:
            return "network"


class UserBehaviorRequest(BaseModel):
    """Schema for user behavior analysis data."""
    user_id: str
    session_duration: conint(ge=0) = 0  # seconds
    commands_executed: conint(ge=0) = 0
    files_accessed: List[str] = []
    login_time_hour: conint(ge=0, le=23) = 12  # 0-23 hour format
    login_source: str = "local"  # "local", "remote", "vpn"
    privilege_escalations: conint(ge=0) = 0
    failed_auth_attempts: conint(ge=0) = 0
    successful_auth_attempts: conint(ge=0) = 1
    unique_source_ips: conint(ge=0) = 1
    data_downloaded_mb: confloat(ge=0) = 0
    data_uploaded_mb: confloat(ge=0) = 0
    sudo_commands: conint(ge=0) = 0
    
    def to_features_dict(self) -> dict:
        """Convert to features dictionary for ML processing."""
        return {k: v for k, v in self.dict().items() if v is not None}


class ProcessMonitorRequest(BaseModel):
    """Schema for process monitoring and anomaly detection."""
    process_name: str
    process_id: conint(ge=1)
    parent_process: str = "unknown"
    user_id: str = "unknown"
    cpu_usage_percent: confloat(ge=0, le=100) = 0
    memory_usage_mb: confloat(ge=0) = 0
    network_connections: conint(ge=0) = 0
    files_opened: conint(ge=0) = 0
    command_line: str = ""
    execution_time_seconds: conint(ge=0) = 0
    child_processes: conint(ge=0) = 0
    is_privileged: bool = False
    syscalls_per_second: confloat(ge=0) = 0
    network_bytes_sent: confloat(ge=0) = 0
    network_bytes_received: confloat(ge=0) = 0
    
    def to_features_dict(self) -> dict:
        """Convert to features dictionary for ML processing."""
        data = self.dict()
        # Add derived features
        data['is_suspicious_name'] = self._is_suspicious_process_name()
        data['is_suspicious_command'] = self._is_suspicious_command_line()
        return {k: v for k, v in data.items() if v is not None}
    
    def _is_suspicious_process_name(self) -> bool:
        """Check if process name looks suspicious."""
        suspicious_patterns = [
            'wget', 'curl', 'nc', 'netcat', 'socat', 'telnet',
            'python -c', 'perl -e', 'bash -c', 'sh -c',
            'base64', 'xxd', 'uuencode', 'openssl'
        ]
        return any(pattern in self.process_name.lower() for pattern in suspicious_patterns)
    
    def _is_suspicious_command_line(self) -> bool:
        """Check if command line contains suspicious patterns."""
        suspicious_patterns = [
            '/tmp/', '/var/tmp/', 'chmod +x', 'wget http',
            'curl -o', '&gt;', 'reverse shell', 'nc -l',
            'python -c "import', '/etc/passwd', '/etc/shadow'
        ]
        return any(pattern in self.command_line.lower() for pattern in suspicious_patterns)

