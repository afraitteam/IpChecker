#!/bin/bash

# متغیرهای عمومی
WEB_ROOT="/var/www/html"
MT_PROXY_DIR="$WEB_ROOT/MTProxy"
NGINX_CONF="/etc/nginx/sites-available/default"
PHP_SCRIPT_URL="https://raw.githubusercontent.com/afraitteam/IpChecker/refs/heads/main/ayhan2"
SYSTEM_USER="www-data"

# بررسی دسترسی روت
if [[ $EUID -ne 0 ]]; then
   echo "این اسکریپت باید با دسترسی روت اجرا شود." 
   exit 1
fi

# به‌روزرسانی و نصب پکیج‌های ضروری
echo "به‌روزرسانی و نصب پکیج‌های ضروری..."
apt update && DEBIAN_FRONTEND=noninteractive apt install -y git build-essential libssl-dev zlib1g-dev nginx php-fpm curl || {
    echo "نصب پکیج‌ها با شکست مواجه شد."
    exit 1
}

# تنظیمات Nginx برای PHP
echo "تنظیمات Nginx برای PHP..."
cat > $NGINX_CONF <<EOF
server {
    listen 80;
    server_name _;  # تنظیم نام سرور (در صورت لزوم می‌توانید این را به دامنه خود تغییر دهید)
    root $WEB_ROOT;

    index index.php index.html index.htm;

    location / {
        try_files \$uri \$uri/ =404;
    }

    location ~ \.php\$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php$(php -r 'echo PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')-fpm.sock;
        fastcgi_param SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
        include fastcgi_params;
    }
}
EOF

# فعال کردن پیکربندی و ری‌استارت Nginx
ln -s $NGINX_CONF /etc/nginx/sites-enabled/ || true
nginx -t && systemctl reload nginx || {
    echo "پیکربندی Nginx با مشکل مواجه شد."
    exit 1
}

# دانلود و ساخت MTProxy
echo "دانلود و ساخت MTProxy..."
rm -rf $MT_PROXY_DIR
git clone https://github.com/TelegramMessenger/MTProxy $MT_PROXY_DIR || {
    echo "دانلود MTProxy با شکست مواجه شد."
    exit 1
}

cd $MT_PROXY_DIR && make || {
    echo "ساخت MTProxy با شکست مواجه شد."
    exit 1
}

# دانلود فایل‌های تنظیمات MTProxy
echo "دانلود فایل‌های تنظیمات MTProxy..."
cd objs/bin
curl -s https://core.telegram.org/getProxySecret -o proxy-secret || {
    echo "دانلود proxy-secret با شکست مواجه شد."
    exit 1
}
curl -s https://core.telegram.org/getProxyConfig -o proxy-multi.conf || {
    echo "دانلود proxy-multi.conf با شکست مواجه شد."
    exit 1
}

# بازگشت به دایرکتوری اصلی
cd $WEB_ROOT

# تنظیم مالکیت و دسترسی‌ها
echo "تنظیم مالکیت و دسترسی‌ها..."
chmod -R 750 $MT_PROXY_DIR
chown -R $SYSTEM_USER:$SYSTEM_USER $WEB_ROOT

# دانلود اسکریپت ayhan.php
echo "دانلود اسکریپت ayhan.php..."
curl -s $PHP_SCRIPT_URL -o ayhan.php || {
    echo "دانلود ayhan.php با شکست مواجه شد."
    exit 1
}
chown $SYSTEM_USER:$SYSTEM_USER ayhan.php

# پیام موفقیت
echo "نصب و پیکربندی با موفقیت انجام شد."

# نمایش لینک دسترسی به فایل
IP_ADDRESS=$(hostname -I | awk '{print $1}')  # دریافت IP محلی
echo "برای دسترسی به MTProxy، فایل ayhan.php را در مرورگر باز کنید:"
echo "http://$IP_ADDRESS/ayhan.php"
