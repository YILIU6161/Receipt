#!/usr/bin/env python3
"""
服务器连接测试脚本
用于诊断服务器访问问题
"""
import socket
import sys
import requests
from urllib.parse import urlparse

def test_port(host, port):
    """测试端口是否开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"端口测试失败: {e}")
        return False

def test_http(url):
    """测试HTTP连接"""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200, response.text[:200]
    except requests.exceptions.ConnectionError:
        return False, "连接被拒绝"
    except requests.exceptions.Timeout:
        return False, "连接超时"
    except Exception as e:
        return False, str(e)

def main():
    if len(sys.argv) < 2:
        print("用法: python test_server.py <服务器地址:端口>")
        print("示例: python test_server.py 192.168.1.100:5000")
        sys.exit(1)
    
    server = sys.argv[1]
    
    # 解析地址
    if ':' in server:
        host, port = server.rsplit(':', 1)
        port = int(port)
    else:
        host = server
        port = 5000
    
    print("=" * 50)
    print("服务器连接诊断")
    print("=" * 50)
    print(f"目标服务器: {host}:{port}")
    print()
    
    # 测试端口
    print("1. 测试端口连接...")
    if test_port(host, port):
        print(f"   ✅ 端口 {port} 已开放")
    else:
        print(f"   ❌ 端口 {port} 无法连接")
        print("   可能原因:")
        print("   - 服务器未启动")
        print("   - 防火墙阻止")
        print("   - 端口配置错误")
        return
    
    # 测试HTTP
    print()
    print("2. 测试HTTP连接...")
    urls = [
        f"http://{host}:{port}/",
        f"http://{host}:{port}/health"
    ]
    
    for url in urls:
        print(f"   测试: {url}")
        success, message = test_http(url)
        if success:
            print(f"   ✅ 连接成功")
        else:
            print(f"   ❌ 连接失败: {message}")
    
    print()
    print("=" * 50)
    print("诊断完成")
    print("=" * 50)

if __name__ == '__main__':
    main()

