# 查看启动日志指南

## 方法1: 直接在终端查看（最简单）

### 直接运行应用

```bash
python3 app.py
```

启动日志会直接显示在终端中，包括：
- 工作目录信息
- 文件检查结果
- 监听地址和端口
- 访问地址
- 运行状态

**注意**: 如果使用这种方式，按 `Ctrl+C` 会停止应用。

### 后台运行并查看日志

```bash
# 后台运行并保存日志
python3 app.py > app.log 2>&1 &

# 查看日志
tail -f app.log

# 查看最后50行
tail -n 50 app.log
```

## 方法2: 使用启动脚本

```bash
# 使用启动脚本（会自动显示日志）
./start_server.sh

# 后台运行并保存日志
nohup ./start_server.sh > server.log 2>&1 &

# 查看日志
tail -f server.log
```

## 方法3: 使用Gunicorn（生产环境）

### 直接运行

```bash
gunicorn -c gunicorn_config.py app:app
```

日志会显示在终端。

### 后台运行并保存日志

```bash
# 后台运行
gunicorn -c gunicorn_config.py app:app --daemon --pid /tmp/gunicorn.pid

# 查看日志（gunicorn_config.py中配置的日志位置）
# 如果配置为 '-'，日志输出到标准输出
# 可以重定向到文件：
gunicorn -c gunicorn_config.py app:app --log-file gunicorn.log --access-logfile access.log
```

## 方法4: 使用systemd服务（推荐生产环境）

### 查看服务日志

```bash
# 查看实时日志
sudo journalctl -u invoice-generator -f

# 查看最近100行
sudo journalctl -u invoice-generator -n 100

# 查看今天的日志
sudo journalctl -u invoice-generator --since today

# 查看最近1小时的日志
sudo journalctl -u invoice-generator --since "1 hour ago"
```

### 查看服务状态

```bash
# 查看服务状态（包含最近日志）
sudo systemctl status invoice-generator

# 查看详细状态
sudo systemctl status invoice-generator -l
```

## 方法5: 检查应用是否运行

### 检查进程

```bash
# 查找Python进程
ps aux | grep python
ps aux | grep gunicorn

# 查找监听5000端口的进程
lsof -i :5000
# 或
netstat -tlnp | grep 5000
# 或
ss -tlnp | grep 5000
```

### 测试应用响应

```bash
# 测试健康检查端点
curl http://127.0.0.1:5000/health

# 测试首页
curl http://127.0.0.1:5000/

# 查看详细响应
curl -v http://127.0.0.1:5000/health
```

## 方法6: 查看错误日志

### Python错误

如果应用启动失败，错误信息会显示在：
- 终端输出（如果直接运行）
- 日志文件（如果重定向）
- systemd日志（如果使用服务）

### 常见错误位置

```bash
# 查看系统日志
sudo journalctl -xe

# 查看Python相关错误
sudo journalctl | grep python

# 查看最近的错误
sudo journalctl -p err -n 50
```

## 实时监控日志

### 使用tail -f

```bash
# 监控日志文件
tail -f app.log

# 监控多个日志文件
tail -f app.log gunicorn.log access.log
```

### 使用multitail（如果已安装）

```bash
# 安装multitail
sudo apt-get install multitail  # Ubuntu/Debian
sudo yum install multitail      # CentOS/RHEL

# 使用multitail监控多个日志
multitail app.log gunicorn.log
```

## 日志文件位置

根据运行方式，日志可能位于：

1. **直接运行**: 终端输出或重定向的文件
2. **Gunicorn**: 
   - 默认: 标准输出
   - 配置后: `gunicorn.log`, `access.log` 等
3. **systemd**: 
   - `journalctl -u invoice-generator`
   - 或配置的日志文件路径

## 快速检查清单

运行以下命令快速检查应用状态：

```bash
# 1. 检查进程
ps aux | grep -E "(python|gunicorn)" | grep app.py

# 2. 检查端口
netstat -tlnp | grep 5000

# 3. 测试连接
curl http://127.0.0.1:5000/health

# 4. 查看最近日志（如果使用systemd）
sudo journalctl -u invoice-generator -n 50

# 5. 查看错误
sudo journalctl -u invoice-generator -p err
```

## 示例：完整的日志查看流程

```bash
# 1. 启动应用（前台运行，查看启动日志）
python3 app.py

# 如果启动成功，会看到：
# ==================================================
# 发票生成器 Web应用
# ==================================================
# 工作目录: /path/to/Project1
# ...
# * Running on http://0.0.0.0:5000

# 2. 在另一个终端测试
curl http://127.0.0.1:5000/health

# 3. 如果使用后台运行
nohup python3 app.py > app.log 2>&1 &

# 4. 查看日志
tail -f app.log

# 5. 检查进程
ps aux | grep python | grep app.py
```

## 故障排查

如果看不到日志：

1. **检查应用是否真的在运行**
   ```bash
   ps aux | grep python
   ```

2. **检查是否有错误**
   ```bash
   python3 app.py 2>&1 | tee app.log
   ```

3. **检查文件权限**
   ```bash
   ls -la app.log
   ```

4. **查看系统日志**
   ```bash
   sudo journalctl -xe
   ```

