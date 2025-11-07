# Hướng dẫn Deploy Production

Hướng dẫn chi tiết để deploy Internal Management System lên production server.

## 🚀 Chuẩn bị

### Yêu cầu hệ thống

- **OS**: Linux (Ubuntu 20.04+, CentOS 7+, Debian 10+)
- **Python**: 3.8 trở lên
- **RAM**: Tối thiểu 512MB (khuyến nghị 1GB+)
- **Disk**: Tối thiểu 1GB (tùy thuộc vào dữ liệu)

### Cài đặt dependencies hệ thống

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx -y
```

**CentOS/RHEL:**
```bash
sudo yum install python3 python3-pip nginx -y
```

## 📦 Deploy Application

### 1. Clone hoặc copy code lên server

```bash
# Clone từ Git
cd /var/www
sudo git clone https://github.com/YOUR_USERNAME/internal_management.git
cd internal_management

# Hoặc copy từ máy local
scp -r /path/to/internal_management user@server:/var/www/
```

### 2. Chạy script deploy

```bash
cd /var/www/internal_management
chmod +x deploy_production.sh
./deploy_production.sh
```

Script này sẽ:
- Tạo virtual environment
- Cài đặt dependencies
- Tạo thư mục data
- Tạo file `.env` với SECRET_KEY ngẫu nhiên

### 3. Cấu hình environment variables

Chỉnh sửa file `.env`:

```bash
nano .env
```

**Quan trọng**: Thay đổi `SECRET_KEY` thành giá trị ngẫu nhiên:

```bash
# Generate SECRET_KEY mới
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

Copy giá trị và paste vào `.env`:

```env
SECRET_KEY=your-generated-secret-key-here
FLASK_ENV=production
HOST=0.0.0.0
PORT=5001
```

### 4. Test chạy thử

```bash
chmod +x run_production.sh
./run_production.sh
```

Truy cập: `http://your-server-ip:5001`

Nếu chạy OK, nhấn `Ctrl+C` để dừng và tiếp tục setup systemd service.

## 🔧 Setup Systemd Service (Khuyến nghị)

### 1. Copy service file

```bash
sudo cp systemd/internal-management.service /etc/systemd/system/
```

### 2. Chỉnh sửa service file

```bash
sudo nano /etc/systemd/system/internal-management.service
```

Thay đổi các giá trị sau cho phù hợp:
- `User` và `Group`: user chạy service (ví dụ: `www-data`, `nginx`, hoặc user riêng)
- `WorkingDirectory`: đường dẫn đến thư mục application
- `EnvironmentFile`: đường dẫn đến file `.env`
- `ExecStart`: đường dẫn đầy đủ đến gunicorn

### 3. Set permissions

```bash
# Tạo user riêng (khuyến nghị)
sudo useradd -r -s /bin/false internal-mgmt

# Set ownership
sudo chown -R internal-mgmt:internal-mgmt /var/www/internal_management

# Set permissions
sudo chmod 755 /var/www/internal_management
sudo chmod -R 750 /var/www/internal_management/data
```

### 4. Enable và start service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (tự động start khi boot)
sudo systemctl enable internal-management

# Start service
sudo systemctl start internal-management

# Kiểm tra status
sudo systemctl status internal-management
```

### 5. Quản lý service

```bash
# Xem logs
sudo journalctl -u internal-management -f

# Restart service
sudo systemctl restart internal-management

# Stop service
sudo systemctl stop internal-management

# Disable service
sudo systemctl disable internal-management
```

## 🌐 Setup Nginx Reverse Proxy (Khuyến nghị)

### 1. Tạo Nginx config

```bash
sudo nano /etc/nginx/sites-available/internal-management
```

Nội dung:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Thay đổi domain của bạn

    # Giới hạn upload size
    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Static files (optional - để Nginx serve static files)
    location /static {
        alias /var/www/internal_management/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 2. Enable site

```bash
# Tạo symbolic link
sudo ln -s /etc/nginx/sites-available/internal-management /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 3. Setup SSL với Let's Encrypt (Khuyến nghị)

```bash
# Cài đặt Certbot
sudo apt install certbot python3-certbot-nginx -y

# Lấy SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal đã được setup tự động
```

## 🔒 Bảo mật

### 1. Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Firewalld (CentOS)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 2. Đổi mật khẩu admin

Sau khi deploy, đăng nhập ngay và đổi mật khẩu admin:
- Username: `admin`
- Password: `admin123`

Vào **Profile > Change Password** để đổi mật khẩu.

### 3. Backup định kỳ

Setup cron job để backup thư mục `data/`:

```bash
# Tạo script backup
sudo nano /usr/local/bin/backup-internal-mgmt.sh
```

Nội dung:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/internal-management"
DATA_DIR="/var/www/internal_management/data"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz -C $(dirname $DATA_DIR) $(basename $DATA_DIR)

# Giữ lại 30 backup gần nhất
ls -t $BACKUP_DIR/backup_*.tar.gz | tail -n +31 | xargs -r rm
```

```bash
# Set permissions
sudo chmod +x /usr/local/bin/backup-internal-mgmt.sh

# Add cron job (backup hàng ngày lúc 2:00 AM)
sudo crontab -e
```

Thêm dòng:
```
0 2 * * * /usr/local/bin/backup-internal-mgmt.sh
```

## 📊 Monitoring

### Xem logs

```bash
# Application logs
tail -f /var/www/internal_management/data/logs/app.log

# Gunicorn access logs
tail -f /var/www/internal_management/data/logs/access.log

# Gunicorn error logs
tail -f /var/www/internal_management/data/logs/error.log

# Systemd logs
sudo journalctl -u internal-management -f
```

### Kiểm tra resource usage

```bash
# CPU & Memory
htop

# Disk usage
df -h
du -sh /var/www/internal_management/data/*
```

## 🔄 Update Application

```bash
# Stop service
sudo systemctl stop internal-management

# Backup data
sudo tar -czf /var/backups/data_backup_$(date +%Y%m%d).tar.gz /var/www/internal_management/data

# Pull latest code
cd /var/www/internal_management
sudo -u internal-mgmt git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements-prod.txt

# Restart service
sudo systemctl start internal-management
```

## ❓ Troubleshooting

### Service không start

```bash
# Xem logs chi tiết
sudo journalctl -u internal-management -n 50 --no-pager

# Kiểm tra permissions
ls -la /var/www/internal_management
ls -la /var/www/internal_management/data
```

### Port đã được sử dụng

```bash
# Kiểm tra port 5001
sudo netstat -tulpn | grep 5001

# Hoặc
sudo lsof -i :5001
```

### Permission denied

```bash
# Fix ownership
sudo chown -R internal-mgmt:internal-mgmt /var/www/internal_management

# Fix permissions
sudo chmod -R 750 /var/www/internal_management/data
```

## 📞 Support

Nếu gặp vấn đề, kiểm tra:
1. Logs trong `data/logs/`
2. Systemd logs: `sudo journalctl -u internal-management`
3. Nginx logs: `/var/log/nginx/error.log`

---

**Lưu ý**: Đây là hướng dẫn cho production deployment. Đảm bảo bạn đã test kỹ trên môi trường staging trước khi deploy lên production.
