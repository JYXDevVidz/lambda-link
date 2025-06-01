import time
import threading
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
import logging

@dataclass
class ClientInfo:
    ipv6: str
    port: int
    last_seen: float
    connection_count: int = 0

class ClientRegistry:
    def __init__(self, timeout: int = 300):
        self._clients: Dict[int, ClientInfo] = {}
        self._lock = threading.RLock()
        self._timeout = timeout
        self._cleanup_thread = threading.Thread(target=self._cleanup_expired, daemon=True)
        self._cleanup_thread.start()
        
    def register_client(self, port: int, ipv6: str) -> bool:
        """注册客户端"""
        try:
            with self._lock:
                self._clients[port] = ClientInfo(
                    ipv6=ipv6,
                    port=port,
                    last_seen=time.time()
                )
                logging.info(f"Client registered: port={port}, ipv6={ipv6}")
                return True
        except Exception as e:
            logging.error(f"Failed to register client: {e}")
            return False
    
    def get_client(self, port: int) -> Optional[ClientInfo]:
        """获取客户端信息"""
        with self._lock:
            client = self._clients.get(port)
            if client and time.time() - client.last_seen < self._timeout:
                return client
            elif client:
                # 客户端已过期
                del self._clients[port]
                logging.info(f"Client expired: port={port}")
            return None
    
    def update_heartbeat(self, port: int) -> bool:
        """更新客户端心跳"""
        with self._lock:
            if port in self._clients:
                self._clients[port].last_seen = time.time()
                return True
            return False
    
    def get_all_clients(self) -> Dict[int, ClientInfo]:
        """获取所有活跃客户端"""
        with self._lock:
            now = time.time()
            active_clients = {}
            for port, client in self._clients.items():
                if now - client.last_seen < self._timeout:
                    active_clients[port] = client
            return active_clients
    
    def _cleanup_expired(self):
        """清理过期客户端"""
        while True:
            try:
                with self._lock:
                    now = time.time()
                    expired_ports = [
                        port for port, client in self._clients.items()
                        if now - client.last_seen >= self._timeout
                    ]
                    for port in expired_ports:
                        del self._clients[port]
                        logging.info(f"Cleaned up expired client: port={port}")
                
                time.sleep(60)  # 每分钟清理一次
            except Exception as e:
                logging.error(f"Cleanup error: {e}")
                time.sleep(60)