import socket
import threading
import logging
import time
from typing import Optional
from .registry import ClientRegistry, ClientInfo
from .utils import is_port_listening

class TCPProxy:
    def __init__(self, registry: ClientRegistry, max_connections: int = 1000):
        self.registry = registry
        self.max_connections = max_connections
        self.active_connections = 0
        self._lock = threading.Lock()
        
    def start_proxy_server(self, port: int):
        """启动指定端口的代理服务"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('0.0.0.0', port))
            server_socket.listen(10)
            
            logging.info(f"Proxy server started on port {port}")
            
            while True:
                try:
                    client_socket, client_addr = server_socket.accept()
                    
                    with self._lock:
                        if self.active_connections >= self.max_connections:
                            client_socket.close()
                            logging.warning(f"Max connections reached, rejected {client_addr}")
                            continue
                        self.active_connections += 1
                    
                    # 创建处理线程
                    thread = threading.Thread(
                        target=self._handle_connection,
                        args=(client_socket, port, client_addr),
                        daemon=True
                    )
                    thread.start()
                    
                except Exception as e:
                    logging.error(f"Error accepting connection on port {port}: {e}")
                    
        except Exception as e:
            logging.error(f"Failed to start proxy server on port {port}: {e}")
    
    def _handle_connection(self, client_socket: socket.socket, port: int, client_addr):
        """处理单个连接"""
        try:
            # 检查是否有本地服务
            if is_port_listening(port):
                logging.info(f"Forwarding to local service: {client_addr} -> 127.0.0.1:{port}")
                self._forward_to_local(client_socket, port)
            else:
                # 查找客户端
                client_info = self.registry.get_client(port)
                if client_info:
                    logging.info(f"Forwarding to client: {client_addr} -> [{client_info.ipv6}]:{port}")
                    self._forward_to_client(client_socket, client_info)
                else:
                    logging.warning(f"No service found for port {port}, closing connection from {client_addr}")
                    client_socket.close()
                    
        except Exception as e:
            logging.error(f"Error handling connection: {e}")
        finally:
            with self._lock:
                self.active_connections -= 1
    
    def _forward_to_local(self, client_socket: socket.socket, port: int):
        """转发到本地服务"""
        try:
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.connect(('127.0.0.1', port))
            
            # 启动双向转发
            self._start_forwarding(client_socket, target_socket)
            
        except Exception as e:
            logging.error(f"Failed to connect to local service on port {port}: {e}")
            client_socket.close()
    
    def _forward_to_client(self, client_socket: socket.socket, client_info: ClientInfo):
        """转发到客户端"""
        try:
            target_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            target_socket.connect((client_info.ipv6, client_info.port))
            
            # 启动双向转发
            self._start_forwarding(client_socket, target_socket)
            
        except Exception as e:
            logging.error(f"Failed to connect to client [{client_info.ipv6}]:{client_info.port}: {e}")
            client_socket.close()
    
    def _start_forwarding(self, sock1: socket.socket, sock2: socket.socket):
        """启动双向数据转发"""
        def forward(src: socket.socket, dst: socket.socket):
            try:
                while True:
                    data = src.recv(4096)
                    if not data:
                        break
                    dst.sendall(data)
            except Exception as e:
                logging.debug(f"Forwarding ended: {e}")
            finally:
                try:
                    src.close()
                    dst.close()
                except:
                    pass
        
        # 启动两个转发线程
        t1 = threading.Thread(target=forward, args=(sock1, sock2), daemon=True)
        t2 = threading.Thread(target=forward, args=(sock2, sock1), daemon=True)
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()