import socket
import netifaces
import subprocess
import logging
from typing import Optional, List

def get_ipv6_addresses() -> List[str]:
    """获取所有IPv6地址"""
    addresses = []
    try:
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface).get(netifaces.AF_INET6, [])
            for addr in addrs:
                ip = addr['addr'].split('%')[0]  # 移除接口后缀
                if not ip.startswith('fe80') and not ip.startswith('::1'):
                    addresses.append(ip)
    except Exception as e:
        logging.error(f"Failed to get IPv6 addresses: {e}")
    return addresses

def get_public_ipv6(interface: Optional[str] = None) -> Optional[str]:
    """获取公网IPv6地址"""
    try:
        addresses = get_ipv6_addresses()
        if not addresses:
            return None
        
        # 如果指定了接口，尝试获取该接口的地址
        if interface:
            try:
                addrs = netifaces.ifaddresses(interface).get(netifaces.AF_INET6, [])
                for addr in addrs:
                    ip = addr['addr'].split('%')[0]
                    if not ip.startswith('fe80') and not ip.startswith('::1'):
                        return ip
            except:
                pass
        
        # 返回第一个可用的IPv6地址
        return addresses[0]
    except Exception as e:
        logging.error(f"Failed to get public IPv6: {e}")
        return None

def test_ipv6_connectivity(ipv6: str, port: int = 80) -> bool:
    """测试IPv6连接性"""
    try:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ipv6, port))
        sock.close()
        return result == 0
    except:
        return False

def is_port_available(port: int) -> bool:
    """检查端口是否可用"""
    try:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('::', port))
        sock.close()
        return True
    except:
        return False