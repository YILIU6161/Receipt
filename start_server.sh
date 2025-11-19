#!/bin/bash
# 启动脚本 - 用于服务器部署

# 设置工作目录
cd "$(dirname "$0")"

echo "=========================================="
echo "发票生成器 - 服务器启动脚本"
echo "=========================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到python3，请先安装Python 3"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"

# 检查依赖是否安装
echo "检查依赖..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "⚠️  依赖未安装，正在安装..."
    python3 -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
fi

echo "✅ 依赖检查完成"

# 检查必要文件
echo "检查项目文件..."
if [ ! -f "app.py" ]; then
    echo "❌ 错误: app.py 不存在"
    exit 1
fi

if [ ! -d "templates" ]; then
    echo "❌ 错误: templates 目录不存在"
    exit 1
fi

if [ ! -d "static" ]; then
    echo "❌ 错误: static 目录不存在"
    exit 1
fi

echo "✅ 项目文件检查完成"

# 设置环境变量
export FLASK_DEBUG=False
export PORT=${PORT:-5000}
export HOST=${HOST:-0.0.0.0}

echo ""
echo "配置信息:"
echo "  端口: $PORT"
echo "  主机: $HOST"
echo "  调试模式: 关闭"
echo ""

# 检查是否使用gunicorn
if command -v gunicorn &> /dev/null; then
    echo "使用Gunicorn启动服务器（生产模式）..."
    echo "=========================================="
    gunicorn -c gunicorn_config.py app:app
else
    echo "使用Flask开发服务器启动..."
    echo "提示: 建议安装gunicorn用于生产环境: pip install gunicorn"
    echo "=========================================="
    python3 app.py
fi

