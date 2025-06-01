#!/bin/bash
set -e

echo "Installing LambdaLink Client..."

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "Python3 is required but not installed"
    exit 1
fi

# 创建目录
mkdir -p /opt/lambdalink/client
mkdir -p /var/log/lambdalink
mkdir -p /etc/lambdalink

# 复制文件
cp -r client/* /opt/lambdalink/client/
cp -r common /opt/lambdalink/

# 安装依赖
cd /opt/lambdalink/client
python3 -m pip install -r requirements.txt

# 创建配置文件
cat > /etc/lambdalink/client.env << EOF
LAMBDALINK_SERVER_HOST=8.217.86.184
LAMBDALINK_API_KEY=198966zql#
LAMBDALINK_LISTEN_PORTS=9000,9001,9002
LAMBDALINK_LOG_LEVEL=INFO
LAMBDALINK_LOG_FILE=/var/log/lambdalink/client.log
EOF

# 创建systemd服务
cat > /etc/systemd/system/lambdalink-client.service << EOF
[Unit]
Description=LambdaLink Client
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/lambdalink
EnvironmentFile=/etc/lambdalink/client.env
ExecStart=/usr/bin/python3 -m client.main
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
systemctl daemon-reload
systemctl enable lambdalink-client

echo "LambdaLink Client installed successfully!"
echo "Edit /etc/lambdalink/client.env to configure"
echo "Start with: systemctl start lambdalink-client"