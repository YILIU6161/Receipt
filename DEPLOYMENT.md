# 服务器部署指南

本文档说明如何在服务器上部署发票生成器Web应用。

## 前置要求

- Python 3.7 或更高版本
- pip（Python包管理器）

## 快速部署

### Linux/macOS 服务器

1. **上传项目文件到服务器**
   ```bash
   # 使用scp或其他方式上传项目目录
   scp -r Project1 user@your-server:/path/to/deploy/
   ```

2. **SSH登录服务器**
   ```bash
   ssh user@your-server
   cd /path/to/deploy/Project1
   ```

3. **安装依赖**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **启动服务器**

   **方式1: 使用启动脚本（推荐）**
   ```bash
   ./start_server.sh
   ```

   **方式2: 使用Gunicorn（生产环境推荐）**
   ```bash
   gunicorn -c gunicorn_config.py app:app
   ```

   **方式3: 直接使用Flask（仅用于测试）**
   ```bash
   python3 app.py
   ```

5. **访问应用**
   - 本地访问: `http://localhost:5000`
   - 外部访问: `http://<服务器IP>:5000`

## 环境变量配置

可以通过环境变量自定义配置：

```bash
# 设置端口（默认5000）
export PORT=5000

# 设置监听地址（默认0.0.0.0，允许外部访问）
export HOST=0.0.0.0

# 设置调试模式（默认False，生产环境应设为False）
export FLASK_DEBUG=False
```

## 使用systemd管理服务（Linux）

创建服务文件 `/etc/systemd/system/invoice-generator.service`:

```ini
[Unit]
Description=Invoice Generator Web Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/deploy/Project1
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="PORT=5000"
Environment="HOST=0.0.0.0"
Environment="FLASK_DEBUG=False"
ExecStart=/usr/local/bin/gunicorn -c /path/to/deploy/Project1/gunicorn_config.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable invoice-generator
sudo systemctl start invoice-generator
sudo systemctl status invoice-generator
```

## 使用Nginx反向代理（推荐）

1. **安装Nginx**
   ```bash
   sudo apt-get update
   sudo apt-get install nginx
   ```

2. **配置Nginx**
   创建配置文件 `/etc/nginx/sites-available/invoice-generator`:

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;  # 替换为你的域名或IP

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       # 静态文件缓存
       location /static {
           alias /path/to/deploy/Project1/static;
           expires 30d;
           add_header Cache-Control "public, immutable";
       }
   }
   ```

3. **启用配置**
   ```bash
   sudo ln -s /etc/nginx/sites-available/invoice-generator /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

## 防火墙配置

确保防火墙允许相应端口：

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 5000/tcp

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

## 故障排查

### 1. 无法访问网页

- **检查服务是否运行**
  ```bash
  ps aux | grep gunicorn
  # 或
  ps aux | grep python
  ```

- **检查端口是否监听**
  ```bash
  netstat -tlnp | grep 5000
  # 或
  ss -tlnp | grep 5000
  ```

- **检查防火墙**
  ```bash
  sudo ufw status
  # 或
  sudo firewall-cmd --list-all
  ```

- **查看日志**
  ```bash
  # Gunicorn日志
  journalctl -u invoice-generator -f
  
  # 或直接查看应用输出
  ```

### 2. 静态文件无法加载

- 检查 `static` 目录是否存在
- 检查文件权限
- 检查Nginx配置（如果使用）

### 3. 文件上传失败

- 检查 `generated_invoices` 和 `uploaded_images` 目录权限
- 确保有写入权限：
  ```bash
  chmod 755 generated_invoices uploaded_images
  ```

### 4. 依赖问题

- 重新安装依赖：
  ```bash
  pip3 install -r requirements.txt --upgrade
  ```

## 安全建议

1. **生产环境不要使用debug模式**
   ```bash
   export FLASK_DEBUG=False
   ```

2. **使用HTTPS**
   - 配置SSL证书
   - 使用Let's Encrypt免费证书

3. **限制文件上传大小**
   - 已在代码中设置最大16MB

4. **定期清理生成的文件**
   ```bash
   # 创建清理脚本
   find generated_invoices -type f -mtime +7 -delete
   ```

5. **使用强密码和密钥**
   - 修改 `app.py` 中的 `SECRET_KEY`

## 性能优化

1. **使用Gunicorn多进程**
   - 已在 `gunicorn_config.py` 中配置

2. **启用Nginx缓存**
   - 静态文件缓存配置

3. **使用CDN**
   - 将静态文件托管到CDN

## 更新应用

```bash
# 1. 停止服务
sudo systemctl stop invoice-generator

# 2. 备份当前版本
cp -r Project1 Project1.backup

# 3. 更新代码
git pull  # 如果使用Git
# 或上传新文件

# 4. 更新依赖（如果需要）
pip3 install -r requirements.txt --upgrade

# 5. 重启服务
sudo systemctl start invoice-generator
```

## 联系支持

如遇到问题，请检查：
1. Python版本是否符合要求
2. 所有依赖是否已安装
3. 端口是否被占用
4. 防火墙配置是否正确
5. 文件权限是否正确

