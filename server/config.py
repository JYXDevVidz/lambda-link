import os
from typing import List

class ServerConfig:
    # 服务端监听配置
    API_HOST = os.getenv('LAMBDALINK_API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('LAMBDALINK_API_PORT', '8000'))
    
    # 代理端口范围
    PROXY_PORTS = list(map(int, os.getenv('LAMBDALINK_PROXY_PORTS', '9000-9010').split('-')))
    if len(PROXY_PORTS) == 2:
        PROXY_PORTS = list(range(PROXY_PORTS[0], PROXY_PORTS[1] + 1))
    
    # 客户端管理
    CLIENT_TIMEOUT = int(os.getenv('LAMBDALINK_CLIENT_TIMEOUT', '300'))  # 5分钟
    HEARTBEAT_INTERVAL = int(os.getenv('LAMBDALINK_HEARTBEAT_INTERVAL', '60'))  # 1分钟
    
    # 安全配置
    API_KEY = os.getenv('LAMBDALINK_API_KEY', 'default-api-key-change-me')
    MAX_CONNECTIONS = int(os.getenv('LAMBDALINK_MAX_CONNECTIONS', '1000'))
    
    # 日志配置
    LOG_LEVEL = os.getenv('LAMBDALINK_LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LAMBDALINK_LOG_FILE', '/var/log/lambdalink-server.log')