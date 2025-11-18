#!/bin/bash
# 启动脚本 - 用于服务器部署

# 设置工作目录
cd "$(dirname "$0")"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3，请先安装Python 3"
    exit 1
fi

# 检查依赖是否安装
if ! python3 -c "import flask" &> /dev/null; then
    echo "正在安装依赖..."
    python3 -m pip install -r requirements.txt
fi

# 设置环境变量
export FLASK_DEBUG=False
export PORT=${PORT:-5000}
export HOST=${HOST:-0.0.0.0}

# 检查是否使用gunicorn
if command -v gunicorn &> /dev/null; then
    echo "使用Gunicorn启动服务器（生产模式）..."
    gunicorn -c gunicorn_config.py app:app
else
    echo "使用Flask开发服务器启动..."
    echo "提示: 建议安装gunicorn用于生产环境: pip install gunicorn"
    python3 app.py
fi

