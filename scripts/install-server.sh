#!/bin/bash
set -e

echo "Installing LambdaLink Server..."

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "Python3 is required but not installed"
    exit 1
fi

# 创建目录
mkdir -p /opt/lambdalink/server
mkdir -p /var/log/lambdalink
mkdir -p /etc/lambdalink

# 复制文件
cp -r server/* /opt/lambdalink/server/
cp -r common /opt/lambdalink/

# 安装依赖
cd /opt/lambdalink/server
python3 -m pip install -r requirements.txt

# 创建配置文件
cat > /etc/lambdalink/server.env << EOF
LAMBDALINK_API_KEY=198966zql#
LAMBDALINK_PROXY_PORTS=9000-9010
LAMBDALINK_LOG_LEVEL=INFO
LAMBDALINK_LOG_FILE=/var/log/lambdalink/server.log
EOF

# 创建systemd服务
cat > /etc/systemd/system/lambdalink-server.service << EOF
[Unit]
Description=LambdaLink Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/lambdalink
EnvironmentFile=/etc/lambdalink/server.env
ExecStart=/usr/bin/python3 -m server.main
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
systemctl daemon-reload
systemctl enable lambdalink-server

echo "LambdaLink Server installed successfully!"
echo "Edit /etc/lambdalink/server.env to configure"
echo "Start with: systemctl start lambdalink-server"