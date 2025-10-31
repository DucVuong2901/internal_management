#!/bin/bash

###############################################################################
# Script Deploy Code từ GitHub lên Proxmox Server
# Sử dụng: ./deploy_proxmox.sh
###############################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="${PROJECT_DIR:-/root/internal_management}"
GIT_REPO="https://github.com/DucVuong2901/internal_management.git"
SERVICE_NAME="internal_management"
APP_PORT=5001

# Print functions
print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "Script phai chay voi quyen root"
        exit 1
    fi
}

# Check if directory exists
check_project_dir() {
    if [ ! -d "$PROJECT_DIR" ]; then
        print_error "Thu muc $PROJECT_DIR khong ton tai!"
        exit 1
    fi
}

# Backup current data
backup_data() {
    print_info "Tao backup..."
    BACKUP_DIR="${PROJECT_DIR}/backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup data directory
    if [ -d "${PROJECT_DIR}/data" ]; then
        cp -r "${PROJECT_DIR}/data" "$BACKUP_DIR/"
        print_success "Backup da duoc tao tai: $BACKUP_DIR"
    fi
    
    # Keep only last 5 backups
    ls -dt ${PROJECT_DIR}/backup_* | tail -n +6 | xargs rm -rf 2>/dev/null || true
}

# Pull code from GitHub
pull_code() {
    print_info "Pull code tu GitHub..."
    
    cd "$PROJECT_DIR"
    
    # Check if git repo
    if [ ! -d ".git" ]; then
        print_warning "Khong phai git repo, clone..."
        cd "$(dirname $PROJECT_DIR)"
        git clone "$GIT_REPO" "$PROJECT_DIR"
        cd "$PROJECT_DIR"
    else
        # Fetch latest
        print_info "Fetching latest code..."
        git fetch origin main
        
        # Check if need update
        LOCAL=$(git rev-parse HEAD)
        REMOTE=$(git rev-parse origin/main)
        
        if [ "$LOCAL" = "$REMOTE" ]; then
            print_warning "Code da la moi nhat!"
            return 0
        fi
        
        # Reset to latest
        print_info "Resetting to latest code..."
        git reset --hard origin/main
        
        print_success "Da pull code moi thanh cong"
    fi
}

# Install dependencies
install_dependencies() {
    print_info "Cai dat dependencies..."
    
    cd "$PROJECT_DIR"
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt --upgrade --quiet
        print_success "Da cai dat dependencies"
    else
        print_warning "Khong tim thay requirements.txt"
    fi
}

# Check if service is running
is_service_running() {
    if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
        return 0
    fi
    
    # Check if process running
    if pgrep -f "app.py" > /dev/null; then
        return 0
    fi
    
    return 1
}

# Start service
start_service() {
    print_info "Khoi dong service..."
    
    # Try systemd first
    if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
        systemctl start "$SERVICE_NAME"
        sleep 2
        if systemctl is-active --quiet "$SERVICE_NAME"; then
            print_success "Service da khoi dong (systemd)"
            return 0
        fi
    fi
    
    # Fallback to manual start
    print_info "Khoi dong manual..."
    cd "$PROJECT_DIR"
    
    # Kill old process
    pkill -f "app.py" 2>/dev/null || true
    sleep 1
    
    # Start new process
    nohup python3 app.py > app.log 2>&1 &
    PID=$!
    
    sleep 3
    
    if ps -p $PID > /dev/null; then
        print_success "Service da khoi dong (manual, PID: $PID)"
        return 0
    else
        print_error "Khong the khoi dong service"
        return 1
    fi
}

# Restart service
restart_service() {
    print_info "Restart service..."
    
    # Try systemd first
    if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
        systemctl restart "$SERVICE_NAME"
        sleep 2
        if systemctl is-active --quiet "$SERVICE_NAME"; then
            print_success "Service da restart (systemd)"
            return 0
        else
            print_warning "Restart systemd that bai, thu khoi dong manual"
        fi
    fi
    
    # Fallback to manual restart
    start_service
}

# Stop service
stop_service() {
    print_info "Dung service..."
    
    # Try systemd first
    if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
        systemctl stop "$SERVICE_NAME"
        print_success "Service da dung (systemd)"
    fi
    
    # Kill manual process
    pkill -f "app.py" 2>/dev/null && print_success "Process da dung (manual)" || print_warning "Khong co process nao dang chay"
}

# Check if app is accessible
check_app() {
    print_info "Kiem tra ung dung..."
    
    sleep 2
    
    # Check port
    if netstat -tuln 2>/dev/null | grep -q ":$APP_PORT "; then
        print_success "Port $APP_PORT dang mo"
    else
        print_warning "Port $APP_PORT chua mo"
    fi
    
    # Try HTTP request
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT | grep -q "200\|302\|301"; then
        print_success "Ung dung dang hoat dong"
        return 0
    else
        print_warning "Ung dung chua phan hoi"
        return 1
    fi
}

# Show logs
show_logs() {
    print_info "Logs:"
    echo ""
    
    # Show last 20 lines
    if [ -f "${PROJECT_DIR}/app.log" ]; then
        tail -20 "${PROJECT_DIR}/app.log"
    else
        journalctl -u "$SERVICE_NAME" -n 20 --no-pager 2>/dev/null || echo "Khong co logs"
    fi
}

# Main function
main() {
    print_header "DEPLOY CODE TU GITHUB LEN PROXMOX"
    
    # Check prerequisites
    print_info "Kiem tra prerequisites..."
    check_root
    check_project_dir
    print_success "Prerequisites OK"
    
    # Backup
    backup_data
    
    # Pull code
    pull_code
    
    # Install dependencies
    install_dependencies
    
    # Restart service
    if is_service_running; then
        restart_service
    else
        start_service
    fi
    
    # Check app
    if check_app; then
        print_header "DEPLOY THANH CONG!"
        echo -e "${GREEN}Ung dung da duoc update va dang chay!${NC}"
    else
        print_header "DEPLOY CO VAN DE!"
        print_error "Ung dung chua hoat dong. Xem logs:"
        show_logs
        exit 1
    fi
    
    # Show status
    echo ""
    print_info "Thong tin:"
    echo "  - Thu muc: $PROJECT_DIR"
    echo "  - Port: $APP_PORT"
    echo ""
    
    # Show logs if needed
    read -p "Ban co muon xem logs? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        show_logs
    fi
}

# Run main
main "$@"

