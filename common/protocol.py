from typing import Dict, Any
from dataclasses import dataclass
import json

@dataclass
class ReportRequest:
    ipv6: str
    port: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'ipv6': self.ipv6,
            'port': self.port
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReportRequest':
        return cls(
            ipv6=data['ipv6'],
            port=data['port']
        )

@dataclass
class HeartbeatRequest:
    port: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {'port': self.port}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HeartbeatRequest':
        return cls(port=data['port'])

@dataclass
class ApiResponse:
    status: str
    message: str = ""
    data: Dict[str, Any] = None
    timestamp: float = 0
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            'status': self.status,
            'timestamp': self.timestamp
        }
        if self.message:
            result['message'] = self.message
        if self.data:
            result['data'] = self.data
        return result