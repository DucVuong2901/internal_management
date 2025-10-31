#!/bin/bash

echo "========================================"
echo "  CAI DAT DEPENDENCIES"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python khong duoc tim thay!"
    echo "Vui long cai dat Python 3.8 tro len truoc."
    exit 1
fi

echo "Checking Python version..."
python3 --version
echo ""

echo "Installing dependencies from requirements.txt..."
echo ""

pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "ERROR: Khong the cai dat dependencies!"
    echo "========================================"
    echo ""
    echo "Thu cac cach sau:"
    echo "1. Su dung: pip3 install --user -r requirements.txt"
    echo "2. Kiem tra ket noi mang"
    echo "3. Su dung sudo (Linux): sudo pip3 install -r requirements.txt"
    echo ""
    exit 1
else
    echo ""
    echo "========================================"
    echo "  CAI DAT THANH CONG!"
    echo "========================================"
    echo ""
    echo "Ban co the chay ung dung bang:"
    echo "  python3 app.py"
    echo "  HOAC"
    echo "  ./run.sh"
    echo ""
fi

