#!/bin/bash

# Fungsi cek dan install package
check_and_install() {
    PACKAGE=$1
    if ! dpkg -s $PACKAGE &> /dev/null; then
        echo "$PACKAGE not found. Installing..."
        sudo apt update -y
        sudo apt install -y $PACKAGE
        echo "$PACKAGE Installed."
    else
        echo "$PACKAGE Installed."
    fi
}

CONF_NAME=$1
DOMAIN=$2
APP_IP=$3

if [ -z "$DOMAIN" ] || [ -z "$APP_IP" ] || [ -z "$CONF_NAME" ]; then
  echo "Usage: $0 <conf_name> <domain_name> <app_ip>"
  echo "Example: $0 example.conf domain.example.com http://localhost:8000"
  exit 1
fi

# Cek dan install nginx
check_and_install nginx
check_and_install certbot
check_and_install python3-certbot-nginx

CONF_FILE="/etc/nginx/conf.d/$CONF_NAME"

# ====== Buat config ======
cat <<EOF > $CONF_FILE
server {
  server_name $DOMAIN;

  server_tokens off;

  add_header X-Frame-Options "SAMEORIGIN" always;
  add_header X-XSS-Protection "1; mode=block" always;
  add_header X-Content-Type-Options "nosniff" always;
  add_header Referrer-Policy "no-referrer-when-downgrade" always;

  location / {
    proxy_pass $APP_IP;
    proxy_redirect     off;
    proxy_set_header   Host \$host;
    proxy_set_header   X-Real-IP \$remote_addr;
    proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Host \$server_name;
    proxy_set_header   X-Forwarded-Proto \$scheme;
  }

  proxy_set_header Upgrade \$http_upgrade;
  proxy_set_header Connection "upgrade";
}
EOF

# ====== Tes config & reload ======
nginx -t && systemctl reload nginx
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN
