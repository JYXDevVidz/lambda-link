import os
from typing import List

class ClientConfig:
    # 服务端配置
    SERVER_HOST = os.getenv('LAMBDALINK_SERVER_HOST', '127.0.0.1')
    SERVER_PORT = int(os.getenv('LAMBDALINK_SERVER_PORT', '8000'))
    API_KEY = os.getenv('LAMBDALINK_API_KEY', 'default-api-key-change-me')
    
    # 客户端配置
    LISTEN_PORTS = list(map(int, os.getenv('LAMBDALINK_LISTEN_PORTS', '9000,9001,9002').split(',')))
    REPORT_INTERVAL = int(os.getenv('LAMBDALINK_REPORT_INTERVAL', '60'))  # 1分钟
    HEARTBEAT_INTERVAL = int(os.getenv('LAMBDALINK_HEARTBEAT_INTERVAL', '30'))  # 30秒
    
    # 网络配置
    IPV6_INTERFACE = os.getenv('LAMBDALINK_IPV6_INTERFACE', None)  # None表示自动检测
    CONNECT_TIMEOUT = int(os.getenv('LAMBDALINK_CONNECT_TIMEOUT', '10'))
    
    # 日志配置
    LOG_LEVEL = os.getenv('LAMBDALINK_LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LAMBDALINK_LOG_FILE', '/var/log/lambdalink-client.log')