#!/bin/bash

# چک کردن اینکه آیا کاربر به عنوان ریشه (root) وارد شده است
if [ "$EUID" -ne 0 ]; then
  echo "لطفا اسکریپت را با دسترسی root اجرا کنید"
  exit
fi

# بروزرسانی بسته‌ها و نصب پیش‌نیازها
echo "Updating system and installing dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv git curl nmap tcpdump telnet

# کلون کردن پروژه از GitHub
echo "Cloning the project from GitHub..."
git clone https://github.com/afraitteam/IpChecker.git /opt/IpChecker

# تغییر دایرکتوری به مسیر پروژه
cd /opt/IpChecker || exit

# ایجاد محیط مجازی و نصب پکیج‌ها
echo "Setting up Python virtual environment and installing requirements..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# ایجاد فایل سرویس systemd
echo "Creating systemd service..."

cat <<EOF >/etc/systemd/system/ipchecker.service
[Unit]
Description=IP Checker Service
After=network.target

[Service]
User=root
WorkingDirectory=/opt/IpChecker
ExecStart=/opt/IpChecker/venv/bin/python3 /opt/IpChecker/Checker.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# راه‌اندازی و فعال کردن سرویس
echo "Enabling and starting the service..."
systemctl daemon-reload
systemctl enable ipchecker.service
systemctl start ipchecker.service

echo "Installation complete. The service is now running and will start on boot."
