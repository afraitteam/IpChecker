#!/bin/bash

# بروزرسانی و نصب پیش‌نیازهای سیستم
echo "Updating system packages..."
sudo apt-get update

echo "Installing necessary system packages..."
sudo apt-get install -y python3 python3-pip git tcpdump nmap

# دانلود پروژه از GitHub
echo "Cloning the project from GitHub..."
git clone https://github.com/afraitteam/IpChecker.git /opt/IpChecker

# وارد شدن به پوشه پروژه
cd /opt/IpChecker

# نصب پیش‌نیازهای پایتون
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# ساخت سرویس systemd
echo "Creating systemd service..."

sudo bash -c 'cat <<EOF > /etc/systemd/system/ipchecker.service
[Unit]
Description=IP Checker Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/IpChecker/app.py
WorkingDirectory=/opt/IpChecker
StandardOutput=inherit
StandardError=inherit
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF'

# فعال‌سازی و شروع سرویس
echo "Enabling and starting the service..."
sudo systemctl enable ipchecker.service
sudo systemctl start ipchecker.service

echo "Installation complete. The service is now running and will start on boot."
