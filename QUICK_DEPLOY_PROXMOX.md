# 🚀 Quick Deploy từ GitHub lên Proxmox

## Cách nhanh nhất để update code

### **Trên Windows (máy dev):**

```bash
# 1. Update code và push lên GitHub
cd D:\internal_management
git add .
git commit -m "Update features"
git push origin main
```

### **Trên Proxmox Server:**

```bash
# 2. SSH vào Proxmox
ssh root@your-proxmox-ip

# 3. Vào container/VM
pct enter 100  # Thay 100 bằng ID container

# 4. Chạy script deploy
cd /root/internal_management
chmod +x deploy_proxmox.sh
./deploy_proxmox.sh
```

**Xong! 🎉**

---

## Hoặc làm thủ công:

```bash
# Vào thư mục
cd /root/internal_management

# Pull code mới
git pull origin main

# Restart app
systemctl restart internal_management
```

---

## Kiểm tra

```bash
# Check service
systemctl status internal_management

# Check logs
journalctl -u internal_management -f

# Test app
curl http://localhost:5001
```

---

**Chi tiết đầy đủ: xem file `DEPLOY_PROXMOX.md`**

