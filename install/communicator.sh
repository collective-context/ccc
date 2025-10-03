#!/bin/bash
# BookStack Installer for Collective Context
# Usage: wget -qO bs io.collective-context.org/communicator && sudo bash bs
# oder:  curl -sL io.collective-context.org/communicator | sudo bash

set -e

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# CC Banner
echo -e "${GREEN}"
cat << "EOF"
   ____      _ _           _   _              ____            _            _   
  / ___|___ | | | ___  ___| |_(_)_   _____   / ___|___  _ __ | |_ _____  _| |_ 
 | |   / _ \| | |/ _ \/ __| __| \ \ / / _ \ | |   / _ \| '_ \| __/ _ \ \/ / __|
 | |__| (_) | | |  __/ (__| |_| |\ V /  __/ | |__| (_) | | | | ||  __/>  <| |_ 
  \____\___/|_|_|\___|\___|\__|_| \_/ \___|  \____\___/|_| |_|\__\___/_/\_\\__|
                                                                                
                    BookStack Installer for CC Ecosystem
                         books.collective-context.org
EOF
echo -e "${NC}"

# Variablen
DOMAIN=${1:-books.collective-context.org}
DB_NAME="bookstack"
DB_USER="bookstack"
DB_PASS=$(openssl rand -base64 32)
APP_KEY=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)
INSTALL_DIR="/var/www/bookstack"
PHP_VERSION="8.2"
BOOKSTACK_VERSION="v24.10"  # Oktober 2025 Version

# System Info
echo -e "${BLUE}[INFO]${NC} System Check..."
echo "Domain: $DOMAIN"
echo "OS: $(lsb_release -ds)"
echo "Kernel: $(uname -r)"
echo "Container: $(systemd-detect-virt || echo 'bare-metal')"
echo ""

# Root Check
if [ "$EUID" -ne 0 ]; then 
   echo -e "${RED}[ERROR]${NC} Bitte als root ausführen (sudo bash bs)"
   exit 1
fi

# Debian 12 Check
if ! grep -q "bookworm" /etc/os-release; then
    echo -e "${YELLOW}[WARN]${NC} Nicht Debian 12 detected. Fortfahren? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}[START]${NC} BookStack Installation für $DOMAIN"

# 1. System Update
echo -e "${BLUE}[1/10]${NC} System Update..."
apt-get update -qq
apt-get upgrade -y -qq

# 2. Dependencies installieren
echo -e "${BLUE}[2/10]${NC} Installing Dependencies..."
apt-get install -y -qq \
    curl \
    git \
    unzip \
    nginx \
    mariadb-server \
    software-properties-common \
    apt-transport-https \
    lsb-release \
    ca-certificates \
    certbot \
    python3-certbot-nginx \
    redis-server \
    supervisor

# 3. PHP 8.2 Installation (Sury Repository)
echo -e "${BLUE}[3/10]${NC} Installing PHP $PHP_VERSION..."
curl -sSL https://packages.sury.org/php/README.txt | bash -x
apt-get update -qq
apt-get install -y -qq \
    php${PHP_VERSION}-fpm \
    php${PHP_VERSION}-cli \
    php${PHP_VERSION}-mbstring \
    php${PHP_VERSION}-xml \
    php${PHP_VERSION}-mysql \
    php${PHP_VERSION}-gd \
    php${PHP_VERSION}-curl \
    php${PHP_VERSION}-zip \
    php${PHP_VERSION}-bcmath \
    php${PHP_VERSION}-intl \
    php${PHP_VERSION}-redis

# 4. MariaDB Setup
echo -e "${BLUE}[4/10]${NC} Configuring MariaDB..."
systemctl start mariadb
systemctl enable mariadb

# Secure Installation
mysql -e "UPDATE mysql.user SET Password=PASSWORD('$DB_PASS') WHERE User='root'"
mysql -e "DELETE FROM mysql.user WHERE User=''"
mysql -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1')"
mysql -e "DROP DATABASE IF EXISTS test"
mysql -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%'"

# Create BookStack Database
mysql -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
mysql -e "CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS'"
mysql -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost'"
mysql -e "FLUSH PRIVILEGES"

# 5. Composer Installation
echo -e "${BLUE}[5/10]${NC} Installing Composer..."
curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# 6. BookStack Download
echo -e "${BLUE}[6/10]${NC} Downloading BookStack $BOOKSTACK_VERSION..."
cd /var/www
git clone https://github.com/BookStackApp/BookStack.git --branch $BOOKSTACK_VERSION --single-branch bookstack
cd $INSTALL_DIR

# 7. BookStack Installation
echo -e "${BLUE}[7/10]${NC} Installing BookStack..."
composer install --no-dev --no-interaction --quiet

# Environment Setup
cp .env.example .env

# Update .env file
cat > .env << EOL
APP_NAME="Collective Context Books"
APP_ENV=production
APP_KEY=base64:$(echo -n $APP_KEY | base64)
APP_DEBUG=false
APP_URL=https://$DOMAIN
APP_THEME=cc-theme

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=$DB_NAME
DB_USERNAME=$DB_USER
DB_PASSWORD=$DB_PASS

MAIL_DRIVER=smtp
MAIL_HOST=localhost
MAIL_PORT=25
MAIL_USERNAME=null
MAIL_PASSWORD=null
MAIL_ENCRYPTION=null

CACHE_DRIVER=redis
SESSION_DRIVER=redis
QUEUE_CONNECTION=redis

REDIS_HOST=127.0.0.1
REDIS_PASSWORD=null
REDIS_PORT=6379

# CC Specific Settings
APP_DEFAULT_DARK_MODE=true
APP_VIEWS_BOOKS=grid
STORAGE_TYPE=local
EOL

# Generate application key
php artisan key:generate --force --no-interaction

# Run migrations
php artisan migrate --force --no-interaction

# 8. Permissions
echo -e "${BLUE}[8/10]${NC} Setting Permissions..."
chown -R www-data:www-data $INSTALL_DIR
chmod -R 755 $INSTALL_DIR
chmod -R 775 $INSTALL_DIR/storage $INSTALL_DIR/bootstrap/cache
chmod -R 640 $INSTALL_DIR/.env

# 9. NGINX Configuration
echo -e "${BLUE}[9/10]${NC} Configuring NGINX..."
cat > /etc/nginx/sites-available/bookstack << 'NGINX'
server {
    listen 80;
    listen [::]:80;
    server_name DOMAIN_PLACEHOLDER;
    
    root /var/www/bookstack/public;
    index index.php index.html;
    
    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }
    
    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_buffers 16 16k;
        fastcgi_buffer_size 32k;
    }
    
    location ~* \.(jpg|jpeg|gif|css|png|js|ico|html)$ {
        access_log off;
        expires max;
        log_not_found off;
    }
    
    location ~ /\.ht {
        deny all;
    }
    
    location ~ /\.(?!well-known).* {
        deny all;
    }
    
    client_max_body_size 50M;
}
NGINX

# Domain in NGINX config ersetzen
sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" /etc/nginx/sites-available/bookstack

# Enable site
ln -sf /etc/nginx/sites-available/bookstack /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload NGINX
nginx -t && systemctl reload nginx

# 10. Optional: SSL mit Let's Encrypt
echo -e "${BLUE}[10/10]${NC} SSL Setup..."
echo -e "${YELLOW}[?]${NC} SSL Zertifikat mit Let's Encrypt einrichten? (y/n)"
read -r ssl_response

if [[ "$ssl_response" =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}[SSL]${NC} Requesting certificate for $DOMAIN..."
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@collective-context.org --redirect
fi

# Create CC Theme Directory
echo -e "${GREEN}[BONUS]${NC} Creating CC Theme..."
mkdir -p $INSTALL_DIR/themes/cc-theme
cat > $INSTALL_DIR/themes/cc-theme/styles.css << 'CSS'
/* Collective Context Theme */
:root {
    --color-primary: #2E7D32;
    --color-primary-dark: #1B5E20;
    --color-primary-light: #4CAF50;
    --color-secondary: #1565C0;
    --color-secondary-dark: #0D47A1;
    --color-secondary-light: #42A5F5;
    --font-body: 'Crimson Text', Georgia, serif;
    --font-heading: 'JetBrains Mono', 'Courier New', monospace;
}

/* Kloster-Style */
.book-content {
    font-family: var(--font-body);
    line-height: 1.8;
    font-size: 1.1em;
}

/* Terminal-Style für Code */
pre, code {
    font-family: var(--font-heading);
    background: #1e1e1e;
    color: #d4d4d4;
}

/* CC Branding */
.navbar-brand:before {
    content: "📚 ";
    font-size: 1.2em;
}
CSS

# Create systemd service for queue worker
cat > /etc/systemd/system/bookstack-queue.service << 'SERVICE'
[Unit]
Description=BookStack Queue Worker
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/bookstack
ExecStart=/usr/bin/php /var/www/bookstack/artisan queue:work --sleep=3 --tries=3
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable bookstack-queue
systemctl start bookstack-queue

# Admin Account erstellen
echo -e "${GREEN}[SETUP]${NC} Creating admin account..."
cd $INSTALL_DIR
php artisan bookstack:create-admin \
    --email="admin@collective-context.org" \
    --name="SysOps" \
    --password="ChangeMeNow2025!" \
    --no-interaction

# Save credentials
cat > /root/bookstack-credentials.txt << CREDS
========================================
   BookStack Installation Complete!
========================================

URL: https://$DOMAIN
Admin: admin@collective-context.org
Password: ChangeMeNow2025!

Database: $DB_NAME
DB User: $DB_USER
DB Pass: $DB_PASS

PHP Version: $PHP_VERSION
BookStack Version: $BOOKSTACK_VERSION

WICHTIG: Bitte Admin-Passwort sofort ändern!

API Tokens generieren:
1. Login als Admin
2. Settings → API Tokens
3. Create Token für CC Commander

========================================
CREDS

# Finale Ausgabe
echo -e "${GREEN}"
echo "========================================="
echo "   BookStack Installation Complete!"
echo "========================================="
echo -e "${NC}"
echo "URL: https://$DOMAIN"
echo "Admin: admin@collective-context.org"
echo "Password: ChangeMeNow2025!"
echo ""
echo -e "${YELLOW}WICHTIG:${NC} Credentials gespeichert in /root/bookstack-credentials.txt"
echo ""
echo -e "${GREEN}Nächste Schritte:${NC}"
echo "1. Login und Admin-Passwort ändern"
echo "2. API Token für CC Commander generieren"
echo "3. Erste Regale und Bücher anlegen"
echo ""
echo -e "${BLUE}CC Commander Integration:${NC}"
echo "ccc bookstack init --url https://$DOMAIN --token YOUR_API_TOKEN"
echo ""
