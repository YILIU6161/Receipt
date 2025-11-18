"""
Gunicorn配置文件 - 用于生产环境部署
"""
import multiprocessing
import os

# 服务器socket
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
backlog = 2048

# 工作进程
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# 日志
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程命名
proc_name = 'invoice_generator'

# 服务器机制
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (如果需要)
# keyfile = None
# certfile = None

