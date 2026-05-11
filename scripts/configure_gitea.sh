#!/bin/bash

# Gitea Configuration for Gen8
# Created: 2026-01-20

GEN8_IP="192.158.1.243"
GITEA_DIR="/home/jonat/services/cicd/gitea"

echo "🔧 Configuring Gitea on Gen8"
echo "=========================="

# Create directories
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "mkdir -p $GITEA_DIR/{data,git,lfs,logs}"

# Create app.ini configuration
cat > /tmp/gitea_app.ini << 'EOF'
APP_NAME = Gen8 Git Hosting
RUN_MODE = prod

[database]
DB_TYPE  = sqlite3
PATH     = /data/gitea/gitea.db

[repository]
ROOT = /data/git/repositories
LFS_STARTUP_SERVER = true
LFS_CONTENT_PATH = /data/lfs

[server]
SSH_DOMAIN       = 192.158.1.243
DOMAIN           = 192.158.1.243
HTTP_PORT        = 3000
ROOT_URL         = http://192.158.1.243:3002/
DISABLE_SSH      = false
SSH_PORT         = 2222
LFS_JWT_SECRET   = gitea_lfs_jwt_secret_change_me
OFFLINE_MODE     = false

[lfs]
PATH = /data/lfs

[security]
INSTALL_LOCK   = true
SECRET_KEY     = gitea_secret_key_change_me
INTERNAL_TOKEN = gitea_internal_token_change_me

[service]
DISABLE_REGISTRATION              = true
REQUIRE_SIGNIN_VIEW              = true
ENABLE_NOTIFY_MAIL              = false
ALLOW_ONLY_EXTERNAL_REGISTRATION = false

[log]
ROOT_PATH = /data/logs
MODE      = file
LEVEL     = info

[picture]
DISABLE_GRAVATAR        = false
ENABLE_FEDERATED_AVATAR = true

[openid]
ENABLE_OPENID_SIGNIN = true
ENABLE_OPENID_SIGNUP = false

[session]
PROVIDER_CONFIG = /data/gitea/sessions
PROVIDER        = file

[log]
MODE      = file
LEVEL     = info
ROOT_PATH = /data/logs

[other]
ENABLE_SITEMAP = true
EOF

# Copy configuration
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "cat > $GITEA_DIR/data/gitea/conf/app.ini" < /tmp/gitea_app.ini

# Set permissions
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "chmod 755 $GITEA_DIR/data/gitea/conf/app.ini"

# Restart Gitea
echo "🔄 Restarting Gitea..."
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "cd /home/jonat/services/cicd && docker-compose restart gitea"

# Wait for startup
sleep 5

echo ""
echo "✅ Gitea Configuration Complete!"
echo ""
echo "🔗 Gitea URL: http://$GEN8_IP:3002"
echo ""
echo "📋 Configuration Details:"
echo "  - Database: SQLite3"
echo "  - SSH Port: 2222"
echo "  - HTTP Port: 3002 (mapped from 3000)"
echo "  - Registration: Disabled"
echo "  - Git LFS: Enabled"
echo ""
echo "👤 First user will be administrator automatically"
echo "🔧 To change settings: Edit $GITEA_DIR/data/gitea/conf/app.ini"
