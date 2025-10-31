# Hướng dẫn Update Code từ GitHub lên Proxmox Server

## 🎯 Tình huống

Bạn đã deploy ứng dụng lên Proxmox server rồi, bây giờ muốn update code mới từ GitHub.

---

## 📋 Các bước Update Code

### **Bước 1: SSH vào Proxmox Server**

```bash
ssh root@your-proxmox-ip
# hoặc
ssh your-username@proxmox-server
```

### **Bước 2: Tìm container/VM chạy ứng dụng**

**Nếu dùng LXC Container:**
```bash
pct list
# Tìm ID của container chạy ứng dụng
```

**Nếu dùng VM:**
```bash
qm list
```

**Vào container/VM:**
```bash
# Với LXC
pct enter CONTAINER_ID

# Với VM, cần SSH vào VM
ssh your-username@vm-ip
```

### **Bước 3: Di chuyển đến thư mục project**

```bash
cd /path/to/internal_management
# Ví dụ: cd /root/internal_management hoặc cd /home/user/internal_management
```

### **Bước 4: Pull code mới từ GitHub**

```bash
# Kiểm tra branch hiện tại
git branch

# Pull code mới từ GitHub
git pull origin main

# Nếu có conflict, reset về version mới nhất
# git fetch origin
# git reset --hard origin/main
```

### **Bước 5: Cài đặt dependencies mới (nếu có)**

```bash
pip install -r requirements.txt --upgrade
```

### **Bước 6: Restart ứng dụng**

**Cách 1: Nếu dùng systemd service**
```bash
systemctl restart internal_management
systemctl status internal_management
```

**Cách 2: Nếu chạy bằng screen/tmux**
```bash
# Tìm screen session
screen -list

# Vào lại session
screen -r SESSION_NAME

# Trong screen, dừng app (Ctrl+C)
# Chạy lại
python3 app.py
# Hoặc
./run.sh
```

**Cách 3: Nếu chạy bằng nohup**
```bash
# Tìm process
ps aux | grep app.py

# Kill process cũ
kill -9 PID

# Chạy lại
nohup python3 app.py > app.log 2>&1 &
```

---

## 🚀 Script Tự Động Deploy

### **Tạo file deploy script:**

```bash
#!/bin/bash
# File: deploy.sh

echo "========================================"
echo "  DEPLOY CODE TU GITHUB"
echo "========================================"

# Thư mục project
PROJECT_DIR="/root/internal_management"
cd $PROJECT_DIR

# Backup trước khi deploy
echo "Backup..."
cp -r data/ data_backup_$(date +%Y%m%d_%H%M%S)/

# Pull code
echo "Pull code tu GitHub..."
git pull origin main

# Check conflict
if [ $? -ne 0 ]; then
    echo "Co conflict! Reset..."
    git fetch origin
    git reset --hard origin/main
fi

# Install dependencies
echo "Install dependencies..."
pip3 install -r requirements.txt --upgrade

# Restart service
echo "Restart service..."
if systemctl is-active --quiet internal_management; then
    systemctl restart internal_management
    echo "Service restarted"
else
    echo "Service khong chay, khoi dong..."
    # Tìm và kill process cũ
    pkill -f app.py
    # Chạy lại
    nohup python3 app.py > app.log 2>&1 &
    echo "Service started"
fi

# Check status
sleep 2
if systemctl is-active --quiet internal_management; then
    echo "========================================"
    echo "  DEPLOY THANH CONG!"
    echo "========================================"
else
    echo "========================================"
    echo "  DEPLOY THAT BAI - CHECK LOGS!"
    echo "========================================"
    tail -20 app.log
fi
```

**Lưu và chạy:**
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 🔧 Các tình huống cụ thể

### **Tình huống 1: Deploy từ Windows lên Proxmox**

**Trên Windows (máy dev):**

1. Commit và push code lên GitHub:
```bash
cd D:\internal_management
git add .
git commit -m "Add new feature"
git push origin main
```

2. SSH vào Proxmox và pull code:
```bash
ssh root@proxmox-ip
pct enter CONTAINER_ID
cd /path/to/internal_management
git pull origin main
systemctl restart internal_management
```

### **Tình huống 2: Tự động deploy từ script**

Tạo file `update_from_github.sh` trên Proxmox:

```bash
#!/bin/bash

CONTAINER_ID="100"  # ID container của bạn
PROJECT_PATH="/root/internal_management"

echo "Deploy to Proxmox..."

# Vào container
pct exec $CONTAINER_ID -- bash -c "
    cd $PROJECT_PATH
    
    # Backup
    cp -r data/ data_backup_\$(date +%Y%m%d_%H%M%S)/
    
    # Pull code
    git pull origin main
    
    # Install dependencies
    pip3 install -r requirements.txt --upgrade
    
    # Restart
    systemctl restart internal_management
"

echo "Done!"
```

### **Tình huống 3: Deploy bằng Webhook**

Tạo endpoint webhook trong app.py:

```python
# Thêm vào app.py

@app.route('/webhook/deploy', methods=['POST'])
def webhook_deploy():
    # Verify secret
    import hmac
    import hashlib
    import subprocess
    
    secret = "your-webhook-secret"  # Set trong environment
    
    signature = request.headers.get('X-Hub-Signature-256', '')
    payload = request.data
    
    mac = hmac.new(
        secret.encode('utf-8'),
        msg=payload,
        digestmod=hashlib.sha256
    )
    
    if not hmac.compare_digest(f"sha256={mac.hexdigest()}", signature):
        return jsonify({'error': 'Invalid signature'}), 403
    
    # Pull và restart
    try:
        result = subprocess.run(
            ['/root/internal_management/deploy.sh'],
            capture_output=True,
            text=True,
            cwd='/root/internal_management'
        )
        
        return jsonify({
            'success': True,
            'output': result.stdout,
            'error': result.stderr
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

Cấu hình trên GitHub:
1. Vào Settings > Webhooks
2. Add webhook
3. URL: `https://your-domain.com/webhook/deploy`
4. Secret: Secret bạn đã set

---

## 📝 Quick Commands

**Deploy nhanh 1 dòng:**
```bash
ssh root@proxmox "pct exec 100 -- bash -c 'cd /root/internal_management && git pull && systemctl restart internal_management'"
```

**Với LXC Container:**
```bash
# SSH vào Proxmox host
ssh root@proxmox-ip

# Vào container
pct enter 100  # Thay 100 bằng ID container của bạn

# Pull code
cd /root/internal_management
git pull origin main

# Restart
systemctl restart internal_management
```

**Với VM:**
```bash
# SSH vào VM
ssh user@vm-ip

# Pull code
cd /path/to/internal_management
git pull origin main

# Restart
systemctl restart internal_management
```

---

## 🐛 Troubleshooting

### **Lỗi: Permission denied**
```bash
chmod -R 755 /path/to/internal_management
chown -R your-user:your-group /path/to/internal_management
```

### **Lỗi: Git not found**
```bash
# Cài Git trong container
apt-get update
apt-get install -y git
```

### **Lỗi: Cannot connect to GitHub**
```bash
# Kiểm tra DNS
ping github.com

# Hoặc dùng SSH thay vì HTTPS
git remote set-url origin git@github.com:DucVuong2901/internal_management.git
```

### **Lỗi: Service không restart**
```bash
# Check logs
journalctl -u internal_management -n 50

# Check service status
systemctl status internal_management

# Check port đã dùng
netstat -tulpn | grep 5001
```

---

## ✅ Checklist Deploy

- [ ] Code đã push lên GitHub
- [ ] SSH vào Proxmox thành công
- [ ] Đã vào container/VM đúng
- [ ] Backup data trước khi deploy
- [ ] Pull code thành công
- [ ] Cài dependencies (nếu có)
- [ ] Restart service
- [ ] Check service running
- [ ] Test ứng dụng hoạt động
- [ ] Check logs không có lỗi

---

## 💡 Tips

1. **Luôn backup trước khi deploy**
2. **Test trên môi trường staging trước**
3. **Monitor logs sau khi deploy**
4. **Có rollback plan**
5. **Sử dụng git tag để version control**

---

## 📞 Liên hệ

Nếu có vấn đề, check logs:
```bash
tail -f /var/log/internal_management/app.log
journalctl -u internal_management -f
```

