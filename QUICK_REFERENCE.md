# Quick Reference - Internal Management System

## 🚀 Cheat Sheet cho Admin

### Development (Local)

```bash
# Chạy development server
python app.py

# Hoặc
./run.bat          # Windows
./run.sh           # Linux/Mac

# Truy cập
http://localhost:5001
```

### Production (Server)

```bash
# Setup lần đầu
./deploy_production.sh

# Chạy manual
./run_production.sh

# Chạy với systemd
sudo systemctl start internal-management
sudo systemctl stop internal-management
sudo systemctl restart internal-management
sudo systemctl status internal-management
```

### Environment Variables

```bash
# Generate SECRET_KEY
python3 -c 'import secrets; print(secrets.token_hex(32))'

# Set environment
export FLASK_ENV=production
export SECRET_KEY=your-generated-key
```

### Logs

```bash
# Application logs
tail -f data/logs/app.log

# Access logs
tail -f data/logs/access.log

# Error logs  
tail -f data/logs/error.log

# Systemd logs
sudo journalctl -u internal-management -f
```

### Backup

```bash
# Manual backup
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz data/

# Restore
tar -xzf backup_20241107_020000.tar.gz

# Backup chỉ database
tar -czf db_backup.tar.gz data/users.csv data/metadata.json data/categories.json data/edit_logs.json
```

### Troubleshooting

```bash
# Check port
sudo netstat -tulpn | grep 5001
sudo lsof -i :5001

# Check processes
ps aux | grep gunicorn
ps aux | grep python

# Check permissions
ls -la data/
ls -la data/logs/

# Fix permissions
sudo chown -R www-data:www-data /var/www/internal_management
sudo chmod -R 750 data/
```

### Nginx

```bash
# Test config
sudo nginx -t

# Reload
sudo systemctl reload nginx

# Restart
sudo systemctl restart nginx

# Logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### Database Operations

```bash
# Xem users
cat data/users.csv

# Xem metadata
cat data/metadata.json | python -m json.tool

# Xem categories
cat data/categories.json

# Xem edit logs (10 gần nhất)
cat data/edit_logs.json | python -m json.tool | tail -n 50
```

### Update Application

```bash
# 1. Backup
sudo tar -czf /var/backups/backup_$(date +%Y%m%d).tar.gz data/

# 2. Stop
sudo systemctl stop internal-management

# 3. Update
git pull
source venv/bin/activate
pip install -r requirements-prod.txt

# 4. Start
sudo systemctl start internal-management

# 5. Verify
sudo systemctl status internal-management
curl http://localhost:5001
```

### Monitoring

```bash
# Disk usage
df -h
du -sh data/*

# Memory usage
free -h

# CPU usage
top
htop

# Service status
sudo systemctl status internal-management

# Check if running
curl http://localhost:5001
```

### Security

```bash
# Firewall (UFW)
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# SSL Certificate (Let's Encrypt)
sudo certbot --nginx -d yourdomain.com
sudo certbot renew --dry-run

# Check SSL expiry
sudo certbot certificates
```

### Common Issues

#### Port already in use
```bash
# Find process
sudo lsof -i :5001

# Kill process
sudo kill -9 <PID>
```

#### Permission denied
```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/internal_management

# Fix permissions
sudo chmod -R 750 data/
```

#### Service won't start
```bash
# Check logs
sudo journalctl -u internal-management -n 50 --no-pager

# Check config
cat /etc/systemd/system/internal-management.service

# Reload daemon
sudo systemctl daemon-reload
```

#### Out of disk space
```bash
# Check disk
df -h

# Clean old logs
find data/logs/ -name "*.log.*" -mtime +30 -delete

# Clean old backups
find /var/backups/ -name "backup_*.tar.gz" -mtime +30 -delete
```

### Performance Tuning

```bash
# Tăng số workers (trong run_production.sh hoặc systemd service)
--workers 8  # 2-4 x số CPU cores

# Tăng timeout
--timeout 300  # 5 phút

# Memory limit
--max-requests 1000  # Restart worker sau 1000 requests
--max-requests-jitter 100
```

### Useful Commands

```bash
# Count users
wc -l data/users.csv

# Count notes
ls data/notes/*.txt | wc -l

# Count docs
ls data/docs/*.txt | wc -l

# Total upload size
du -sh data/uploads/

# Recent activity (from logs)
tail -n 100 data/edit_logs.json | grep -o '"action":"[^"]*"' | sort | uniq -c
```

### Default Credentials

```
Username: admin
Password: admin123
```

**⚠️ QUAN TRỌNG: Đổi mật khẩu ngay sau lần đăng nhập đầu tiên!**

### Important Files

```
data/users.csv          # User database
data/metadata.json      # Notes & docs metadata
data/categories.json    # Categories
data/edit_logs.json     # Edit history
data/notes/*.txt        # Note contents
data/docs/*.txt         # Document contents
data/uploads/           # Attachments
data/logs/              # Application logs
.env                    # Environment variables (KHÔNG commit)
```

### Support

- **Documentation**: `PRODUCTION_DEPLOY.md`, `OPTIMIZATION_SUMMARY.md`
- **Logs**: `data/logs/`
- **Backup**: `BACKUP_GUIDE.md`

---

**Tip**: Bookmark file này để tham khảo nhanh khi cần!
