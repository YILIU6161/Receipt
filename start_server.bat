@echo off
REM 启动脚本 - Windows版本

REM 设置工作目录
cd /d "%~dp0"

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到python，请先安装Python 3
    exit /b 1
)

REM 检查依赖是否安装
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    python -m pip install -r requirements.txt
)

REM 设置环境变量
set FLASK_DEBUG=False
set PORT=5000
set HOST=0.0.0.0

REM 启动服务器
echo 启动Flask服务器...
python app.py

