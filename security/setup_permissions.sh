#!/bin/bash
# Security Setup Script
# Sets up proper permissions for security files

echo "Setting up security permissions..."

# Secure .env file
chmod 600 /home/jonat/ai-stack/.env
echo "✅ .env file permissions set to 600"

# Create logs directory with proper permissions
mkdir -p /home/jonat/ai-stack/logs
chmod 755 /home/jonat/ai-stack/logs
echo "✅ logs directory permissions set to 755"

# Set permissions on security files
chmod 755 /home/jonat/ai-stack/security
chmod 644 /home/jonat/ai-stack/security/*.py
echo "✅ security directory permissions set"

# Set permissions on logging files
chmod 755 /home/jonat/ai-stack/logging
chmod 644 /home/jonat/ai-stack/logging/*.py
echo "✅ logging directory permissions set"

# Create log files with restricted permissions
touch /home/jonat/ai-stack/logs/security.log
touch /home/jonat/ai-stack/logs/performance.log
touch /home/jonat/ai-stack/logs/errors.log
touch /home/jonat/ai-stack/logs/audit.log

chmod 640 /home/jonat/ai-stack/logs/*.log
echo "✅ log files permissions set to 640"

# Set ownership
chown -R jonat:jonat /home/jonat/ai-stack/security
chown -R jonat:jonat /home/jonat/ai-stack/logging
chown -R jonat:jonat /home/jonat/ai-stack/logs
echo "✅ ownership set to jonat:jonat"

# Verify permissions
echo ""
echo "🔒 Permission Verification:"
ls -la /home/jonat/ai-stack/.env
echo ""
ls -la /home/jonat/ai-stack/logs/
echo ""
echo "Security setup complete!"
