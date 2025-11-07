#!/bin/bash
# Script deploy production cho Internal Management System

echo "=========================================="
echo "Deploy Internal Management System"
echo "=========================================="

# Kiểm tra Python version
echo "Checking Python version..."
python3 --version || { echo "Python 3 is required!"; exit 1; }

# Tạo virtual environment nếu chưa có
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Cài đặt dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements-prod.txt

# Tạo thư mục data nếu chưa có
echo "Creating data directories..."
mkdir -p data/{notes,docs,uploads/{notes,docs},logs}

# Kiểm tra file .env
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Flask Environment
FLASK_ENV=production

# Secret Key - PHẢI thay đổi giá trị này!
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# Server Configuration
HOST=0.0.0.0
PORT=5001

# Domain (optional)
# DOMAIN_NAME=yourdomain.com

# Edit logs retention (days)
EDIT_LOGS_RETENTION_DAYS=30
EOF
    echo "✓ Created .env file with random SECRET_KEY"
    echo "⚠ Please review and update .env file if needed"
fi

# Set permissions
echo "Setting permissions..."
chmod 755 wsgi.py
chmod 755 deploy_production.sh

echo ""
echo "=========================================="
echo "✓ Deployment preparation completed!"
echo "=========================================="
echo ""
echo "To run with Gunicorn:"
echo "  gunicorn --bind 0.0.0.0:5001 --workers 4 --timeout 120 wsgi:application"
echo ""
echo "Or use the run_production.sh script:"
echo "  ./run_production.sh"
echo ""
echo "To run as systemd service, see: systemd/internal-management.service"
echo "=========================================="
