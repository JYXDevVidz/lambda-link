import subprocess
import socket
import logging
from typing import Optional

def is_port_listening(port: int, host: str = '127.0.0.1') -> bool:
    """检查指定端口是否被本地服务监听"""
    try:
        # 使用ss命令检查端口
        result = subprocess.run(
            ['ss', '-lnt', f'sport = :{port}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return bool(result.stdout.strip())
    except Exception as e:
        logging.warning(f"Failed to check port {port}: {e}")
        # 备用方法：尝试连接
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False

def validate_ipv6(address: str) -> bool:
    """验证IPv6地址格式"""
    try:
        socket.inet_pton(socket.AF_INET6, address)
        return True
    except socket.error:
        return False

def get_local_ip() -> str:
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"