import requests
import time
import threading
import logging
from typing import Optional
from .config import ClientConfig
from .utils import get_public_ipv6

class ClientReporter:
    def __init__(self):
        self.server_url = f"http://{ClientConfig.SERVER_HOST}:{ClientConfig.SERVER_PORT}"
        self.headers = {
            'X-API-Key': ClientConfig.API_KEY,
            'Content-Type': 'application/json'
        }
        self.current_ipv6: Optional[str] = None
        self.running = False
        
    def start(self):
        """启动上报服务"""
        self.running = True
        
        # 启动初始注册
        self._initial_report()
        
        # 启动定期上报线程
        report_thread = threading.Thread(target=self._report_loop, daemon=True)
        report_thread.start()
        
        # 启动心跳线程
        heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        heartbeat_thread.start()
        
        logging.info("Client reporter started")
    
    def stop(self):
        """停止上报服务"""
        self.running = False
        logging.info("Client reporter stopped")
    
    def _initial_report(self):
        """初始注册"""
        ipv6 = get_public_ipv6(ClientConfig.IPV6_INTERFACE)
        if not ipv6:
            logging.error("Failed to get IPv6 address")
            return
        
        self.current_ipv6 = ipv6
        logging.info(f"Detected IPv6 address: {ipv6}")
        
        # 注册所有端口
        for port in ClientConfig.LISTEN_PORTS:
            self._report_client(ipv6, port)
    
    def _report_client(self, ipv6: str, port: int) -> bool:
        """上报客户端信息"""
        try:
            data = {
                'ipv6': ipv6,
                'port': port
            }
            
            response = requests.post(
                f"{self.server_url}/api/report",
                json=data,
                headers=self.headers,
                timeout=ClientConfig.CONNECT_TIMEOUT
            )
            
            if response.status_code == 200:
                logging.info(f"Successfully reported: port={port}, ipv6={ipv6}")
                return True
            else:
                logging.error(f"Failed to report port {port}: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Error reporting port {port}: {e}")
            return False
    
    def _send_heartbeat(self, port: int) -> bool:
        """发送心跳"""
        try:
            data = {'port': port}
            response = requests.post(
                f"{self.server_url}/api/heartbeat",
                json=data,
                headers=self.headers,
                timeout=ClientConfig.CONNECT_TIMEOUT
            )
            
            if response.status_code == 200:
                logging.debug(f"Heartbeat sent for port {port}")
                return True
            else:
                logging.warning(f"Heartbeat failed for port {port}: {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"Error sending heartbeat for port {port}: {e}")
            return False
    
    def _report_loop(self):
        """定期上报循环"""
        while self.running:
            try:
                # 检查IPv6地址是否变化
                new_ipv6 = get_public_ipv6(ClientConfig.IPV6_INTERFACE)
                if new_ipv6 and new_ipv6 != self.current_ipv6:
                    logging.info(f"IPv6 address changed: {self.current_ipv6} -> {new_ipv6}")
                    self.current_ipv6 = new_ipv6
                    
                    # 重新注册所有端口
                    for port in ClientConfig.LISTEN_PORTS:
                        self._report_client(new_ipv6, port)
                
                time.sleep(ClientConfig.REPORT_INTERVAL)
                
            except Exception as e:
                logging.error(f"Error in report loop: {e}")
                time.sleep(ClientConfig.REPORT_INTERVAL)
    
    def _heartbeat_loop(self):
        """心跳循环"""
        while self.running:
            try:
                for port in ClientConfig.LISTEN_PORTS:
                    self._send_heartbeat(port)
                
                time.sleep(ClientConfig.HEARTBEAT_INTERVAL)
                
            except Exception as e:
                logging.error(f"Error in heartbeat loop: {e}")
                time.sleep(ClientConfig.HEARTBEAT_INTERVAL)