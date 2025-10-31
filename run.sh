#!/bin/bash

echo "========================================"
echo "  HE THONG QUAN LY NOI BO"
echo "  Starting Application..."
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python khong duoc tim thay!"
    echo "Vui long cai dat Python 3.8 tro len."
    exit 1
fi

echo "Checking Python version..."
python3 --version

echo ""
echo "Checking dependencies..."
if ! pip3 show Flask &> /dev/null; then
    echo "Dependencies chua duoc cai dat!"
    echo "Dang cai dat dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Khong the cai dat dependencies!"
        exit 1
    fi
    echo "Dependencies da duoc cai dat thanh cong!"
else
    echo "Dependencies da san sang!"
fi

echo ""
echo "========================================"
echo "  Starting Flask Application..."
if [ -n "$DOMAIN_NAME" ]; then
    echo "  Using domain: $DOMAIN_NAME"
    echo "  Access at: http://$DOMAIN_NAME:5001"
else
    echo "  Access at: http://localhost:5001"
    echo "  To use custom domain: export DOMAIN_NAME=yourdomain.com"
fi
echo "  Press CTRL+C to stop"
echo "========================================"
echo ""

python3 app.py

