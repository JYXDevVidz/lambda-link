#!/usr/bin/env python3
import logging
import threading
import time
from flask import Flask, request, jsonify
from .config import ServerConfig
from .registry import ClientRegistry
from .proxy import TCPProxy
from .utils import validate_ipv6
from common.logger import setup_logger

# 初始化日志
setup_logger(ServerConfig.LOG_LEVEL, ServerConfig.LOG_FILE)

# 初始化组件
registry = ClientRegistry(ServerConfig.CLIENT_TIMEOUT)
proxy = TCPProxy(registry, ServerConfig.MAX_CONNECTIONS)

# Flask应用
app = Flask(__name__)

def verify_api_key():
    """验证API密钥"""
    api_key = request.headers.get('X-API-Key')
    if api_key != ServerConfig.API_KEY:
        return False
    return True

@app.route('/api/report', methods=['POST'])
def report_client():
    """客户端上报接口"""
    if not verify_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        ipv6 = data.get('ipv6')
        port = data.get('port')
        
        if not ipv6 or not port:
            return jsonify({'error': 'Missing ipv6 or port'}), 400
        
        if not validate_ipv6(ipv6):
            return jsonify({'error': 'Invalid IPv6 address'}), 400
        
        if not (1 <= port <= 65535):
            return jsonify({'error': 'Invalid port number'}), 400
        
        # 注册客户端
        success = registry.register_client(port, ipv6)
        if success:
            return jsonify({'status': 'registered', 'timestamp': time.time()})
        else:
            return jsonify({'error': 'Registration failed'}), 500
            
    except Exception as e:
        logging.error(f"Report error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    """心跳接口"""
    if not verify_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        data = request.get_json()
        port = data.get('port')
        
        if not port:
            return jsonify({'error': 'Missing port'}), 400
        
        success = registry.update_heartbeat(port)
        if success:
            return jsonify({'status': 'ok', 'timestamp': time.time()})
        else:
            return jsonify({'error': 'Client not found'}), 404
            
    except Exception as e:
        logging.error(f"Heartbeat error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/clients', methods=['GET'])
def get_clients():
    """获取客户端列表"""
    if not verify_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        clients = registry.get_all_clients()
        result = {}
        for port, client in clients.items():
            result[port] = {
                'ipv6': client.ipv6,
                'port': client.port,
                'last_seen': client.last_seen,
                'connection_count': client.connection_count
            }
        return jsonify(result)
    except Exception as e:
        logging.error(f"Get clients error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取服务状态"""
    try:
        clients = registry.get_all_clients()
        return jsonify({
            'status': 'running',
            'timestamp': time.time(),
            'active_clients': len(clients),
            'proxy_ports': ServerConfig.PROXY_PORTS,
            'active_connections': proxy.active_connections
        })
    except Exception as e:
        logging.error(f"Status error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def start_proxy_servers():
    """启动所有代理服务器"""
    for port in ServerConfig.PROXY_PORTS:
        thread = threading.Thread(
            target=proxy.start_proxy_server,
            args=(port,),
            daemon=True
        )
        thread.start()
        logging.info(f"Started proxy server thread for port {port}")

if __name__ == '__main__':
    logging.info("Starting LambdaLink Server v1.0")
    
    # 启动代理服务器
    start_proxy_servers()
    
    # 启动API服务器
    app.run(
        host=ServerConfig.API_HOST,
        port=ServerConfig.API_PORT,
        debug=False,
        threaded=True
    )