#!/bin/bash
# Update and install necessary packages
sudo apt update && sudo DEBIAN_FRONTEND=noninteractive apt install -y git build-essential libssl-dev zlib1g-dev apache2 php libapache2-mod-php 
# Navigate to the web root directory
cd /var/www/html 
# Remove any existing MTProxy directory
sudo rm -rf MTProxy 
# Clone and build MTProxy
sudo git clone https://github.com/TelegramMessenger/MTProxy 
cd MTProxy 
sudo make 
# Fetch proxy secrets and configurations
cd objs/bin 
sudo curl -s https://core.telegram.org/getProxySecret -o proxy-secret 
sudo curl -s https://core.telegram.org/getProxyConfig -o proxy-multi.conf 
cd ../../.. 
# Set permissions and download additional script
sudo chmod 777 -R * 
sudo curl -s https://raw.githubusercontent.com/afraitteam/IpChecker/refs/heads/main/ayhan2 -o ayhan.php 
# Change owner and update sudoers file
sudo chown www-data:www-data -R * 
sudo adduser www-data sudo 
echo 'www-data ALL=(ALL) NOPASSWD:ALL' | sudo tee -a /etc/sudoers > /dev/null

