# 故障排查指南

如果服务器上运行app.py后网页无法访问，请按照以下步骤排查：

## 1. 检查应用是否正常启动

### 查看启动日志

运行应用时，应该看到类似以下的输出：

```
==================================================
发票生成器 Web应用
==================================================
工作目录: /path/to/Project1
模板目录: /path/to/Project1/templates
静态目录: /path/to/Project1/static
✅ 模板文件: /path/to/Project1/templates/index.html
✅ 静态文件: /path/to/Project1/static/css/style.css
运行模式: 生产模式
监听地址: 0.0.0.0:5000
本地访问: http://127.0.0.1:5000
外部访问: http://<服务器IP>:5000
健康检查: http://localhost:5000/health
按 Ctrl+C 停止服务器
==================================================
 * Running on http://0.0.0.0:5000
```

**如果没有看到 "Running on" 消息，说明应用启动失败。**

### 检查错误信息

如果启动失败，查看是否有错误信息：
- 端口被占用
- 文件路径错误
- 依赖缺失
- Python版本不兼容

## 2. 在服务器本地测试

### 方法1: 使用curl测试

```bash
# 测试首页
curl http://127.0.0.1:5000/

# 测试健康检查端点
curl http://127.0.0.1:5000/health
```

如果本地可以访问，说明应用运行正常，问题在外部访问。

### 方法2: 使用wget测试

```bash
wget http://127.0.0.1:5000/health
```

### 方法3: 使用Python测试脚本

```bash
python3 test_server.py 127.0.0.1:5000
```

## 3. 检查网络配置

### 检查监听地址

应用应该监听 `0.0.0.0`，而不是 `127.0.0.1`：

```bash
# 检查端口监听情况
netstat -tlnp | grep 5000
# 或
ss -tlnp | grep 5000
```

应该看到类似：
```
tcp  0  0  0.0.0.0:5000  0.0.0.0:*  LISTEN  12345/python
```

如果看到 `127.0.0.1:5000`，说明只监听本地，外部无法访问。

### 检查服务器IP

```bash
# 获取服务器IP地址
hostname -I
# 或
ip addr show
# 或
ifconfig
```

## 4. 检查防火墙

### Ubuntu/Debian (ufw)

```bash
# 检查状态
sudo ufw status

# 允许端口
sudo ufw allow 5000/tcp

# 重新加载
sudo ufw reload
```

### CentOS/RHEL (firewalld)

```bash
# 检查状态
sudo firewall-cmd --list-all

# 允许端口
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

### iptables

```bash
# 检查规则
sudo iptables -L -n

# 添加规则（临时）
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

## 5. 检查云服务器安全组

如果使用云服务器（阿里云、腾讯云、AWS等），需要：

1. 登录云服务器控制台
2. 找到安全组配置
3. 添加入站规则：允许TCP端口5000
4. 保存规则

## 6. 检查应用配置

### 确认环境变量

```bash
# 检查环境变量
echo $PORT
echo $HOST
echo $FLASK_DEBUG
```

### 手动设置环境变量

```bash
export HOST=0.0.0.0
export PORT=5000
export FLASK_DEBUG=False
python3 app.py
```

## 7. 使用Gunicorn（推荐生产环境）

Flask开发服务器可能在某些环境下不稳定，建议使用Gunicorn：

```bash
# 安装gunicorn
pip3 install gunicorn

# 使用gunicorn启动
gunicorn -c gunicorn_config.py app:app

# 或直接启动
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 8. 检查文件权限

```bash
# 确保脚本有执行权限
chmod +x start_server.sh

# 确保目录有读写权限
chmod 755 generated_invoices
chmod 755 uploaded_images
```

## 9. 使用systemd服务（推荐）

创建服务文件可以更好地管理应用：

```bash
sudo nano /etc/systemd/system/invoice-generator.service
```

内容：
```ini
[Unit]
Description=Invoice Generator Web Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/Project1
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="PORT=5000"
Environment="HOST=0.0.0.0"
Environment="FLASK_DEBUG=False"
ExecStart=/usr/local/bin/gunicorn -c /path/to/Project1/gunicorn_config.py app:app
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

查看日志：
```bash
sudo journalctl -u invoice-generator -f
```

## 10. 常见错误及解决方案

### 错误1: "Address already in use"

**原因**: 端口被占用

**解决**:
```bash
# 查找占用端口的进程
lsof -i :5000
# 或
netstat -tlnp | grep 5000

# 杀死进程
kill -9 <PID>
```

### 错误2: "ModuleNotFoundError"

**原因**: 依赖未安装

**解决**:
```bash
pip3 install -r requirements.txt
```

### 错误3: "Template not found"

**原因**: 模板文件路径错误

**解决**: 确保在项目根目录运行，且templates目录存在

### 错误4: 外部无法访问但本地可以

**原因**: 
- 监听地址是127.0.0.1而不是0.0.0.0
- 防火墙阻止
- 安全组未配置

**解决**: 检查HOST环境变量，确保设置为0.0.0.0

## 11. 调试步骤总结

1. ✅ 检查应用是否启动（查看日志）
2. ✅ 本地测试（curl http://127.0.0.1:5000）
3. ✅ 检查监听地址（netstat/ss）
4. ✅ 检查防火墙（ufw/firewall-cmd）
5. ✅ 检查云服务器安全组
6. ✅ 使用Gunicorn替代Flask开发服务器
7. ✅ 查看详细错误日志

## 12. 获取帮助

如果以上步骤都无法解决问题，请提供：

1. 启动时的完整日志输出
2. `netstat -tlnp | grep 5000` 的输出
3. `curl http://127.0.0.1:5000/health` 的输出
4. 服务器操作系统版本
5. Python版本 (`python3 --version`)
6. 错误信息（如果有）

