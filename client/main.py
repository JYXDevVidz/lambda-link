#!/usr/bin/env python3
import signal
import sys
import logging
import time
from .config import ClientConfig
from .reporter import ClientReporter
from .listener import PortListener
from .utils import get_public_ipv6, is_port_available
from common.logger import setup_logger

# 初始化日志
setup_logger(ClientConfig.LOG_LEVEL, ClientConfig.LOG_FILE)

class LambdaLinkClient:
    def __init__(self):
        self.reporter = ClientReporter()
        self.listener = PortListener()
        self.running = False
    
    def start(self):
        """启动客户端"""
        logging.info("Starting LambdaLink Client v1.0")
        
        # 检查IPv6地址
        ipv6 = get_public_ipv6(ClientConfig.IPV6_INTERFACE)
        if not ipv6:
            logging.error("No IPv6 address available, cannot start client")
            return False
        
        # 检查端口可用性
        for port in ClientConfig.LISTEN_PORTS:
            if not is_port_available(port):
                logging.error(f"Port {port} is not available")
                return False
        
        logging.info(f"Client IPv6: {ipv6}")
        logging.info(f"Listen ports: {ClientConfig.LISTEN_PORTS}")
        logging.info(f"Server: {ClientConfig.SERVER_HOST}:{ClientConfig.SERVER_PORT}")
        
        # 启动组件
        self.running = True
        
        try:
            # 启动端口监听
            self.listener.start()
            
            # 启动上报服务
            self.reporter.start()
            
            logging.info("Client started successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to start client: {e}")
            self.stop()
            return False
    
    def stop(self):
        """停止客户端"""
        if self.running:
            logging.info("Stopping LambdaLink Client")
            self.running = False
            
            self.reporter.stop()
            self.listener.stop()
            
            logging.info("Client stopped")
    
    def run(self):
        """运行客户端"""
        if not self.start():
            sys.exit(1)
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Received interrupt signal")
        finally:
            self.stop()

def signal_handler(signum, frame):
    """信号处理"""
    logging.info(f"Received signal {signum}")
    client.stop()
    sys.exit(0)

# 全局客户端实例
client = LambdaLinkClient()

if __name__ == '__main__':
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 运行客户端
    client.run()