#!/usr/bin/env python3
"""
Flask Web应用 - 发票生成器前端
"""
from flask import Flask, render_template, request, send_file, jsonify, make_response
from invoice_generator import create_invoice
from datetime import datetime, timedelta
import os
import uuid

app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static',
            template_folder='templates')
app.config['SECRET_KEY'] = 'your-secret-key-here'
# 使用绝对路径确保在服务器上正常工作
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'generated_invoices')
app.config['UPLOAD_IMAGES'] = os.path.join(BASE_DIR, 'uploaded_images')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 添加响应头以支持Chrome浏览器
@app.after_request
def after_request(response):
    """添加必要的HTTP响应头"""
    # 允许跨域（如果需要）
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    
    # 安全策略头
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # 确保正确的Content-Type
    if response.content_type and 'text/html' in response.content_type:
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
    elif response.content_type and 'application/json' in response.content_type:
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
    
    return response

# 确保输出目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['UPLOAD_IMAGES'], exist_ok=True)

# 允许的图片扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """首页 - 显示发票表单"""
    response = make_response(render_template('index.html'))
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response


@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({'status': 'ok', 'message': '服务运行正常'}), 200


@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    """处理OPTIONS预检请求"""
    response = make_response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


@app.route('/generate', methods=['POST'])
def generate_invoice():
    """处理表单提交并生成发票"""
    try:
        # 获取表单数据
        data = request.form
        
        # 处理文件上传 - Logo
        logo_path = None
        if 'company_logo' in request.files:
            logo_file = request.files['company_logo']
            if logo_file and logo_file.filename:
                # 检查文件扩展名
                if not allowed_file(logo_file.filename):
                    return jsonify({
                        'success': False,
                        'error': f'Invalid logo file format. Allowed formats: {", ".join(ALLOWED_EXTENSIONS)}'
                    }), 400
                
                try:
                    logo_filename = f"logo_{uuid.uuid4().hex[:8]}_{logo_file.filename}"
                    logo_path = os.path.join(app.config['UPLOAD_IMAGES'], logo_filename)
                    logo_file.save(logo_path)
                    # 验证文件是否成功保存
                    if not os.path.exists(logo_path):
                        logo_path = None
                        return jsonify({
                            'success': False,
                            'error': 'Failed to save logo file'
                        }), 400
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'error': f'Error saving logo: {str(e)}'
                    }), 400
        
        # 处理文件上传 - 图章
        stamp_path = None
        if 'company_stamp' in request.files:
            stamp_file = request.files['company_stamp']
            if stamp_file and stamp_file.filename:
                # 检查文件扩展名
                if not allowed_file(stamp_file.filename):
                    return jsonify({
                        'success': False,
                        'error': f'Invalid stamp file format. Allowed formats: {", ".join(ALLOWED_EXTENSIONS)}'
                    }), 400
                
                try:
                    stamp_filename = f"stamp_{uuid.uuid4().hex[:8]}_{stamp_file.filename}"
                    stamp_path = os.path.join(app.config['UPLOAD_IMAGES'], stamp_filename)
                    stamp_file.save(stamp_path)
                    # 验证文件是否成功保存
                    if not os.path.exists(stamp_path):
                        stamp_path = None
                        return jsonify({
                            'success': False,
                            'error': 'Failed to save stamp file'
                        }), 400
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'error': f'Error saving stamp: {str(e)}'
                    }), 400
        
        # 公司信息
        company_info = {
            'name': data.get('company_name', ''),
            'address': data.get('company_address', ''),
            'phone': data.get('company_phone', ''),
            'email': data.get('company_email', '')
        }
        
        # 发货方信息（可选）
        shipper_info = None
        if data.get('shipper_name'):
            shipper_info = {
                'name': data.get('shipper_name', ''),
                'address': data.get('shipper_address', ''),
                'phone': data.get('shipper_phone', '')
            }
        
        # 客户信息（Consignee/Buyer）
        customer_info = {
            'name': data.get('customer_name', ''),
            'address': data.get('customer_address', ''),
            'phone': data.get('customer_phone', ''),
            'email': data.get('customer_email', ''),
            'plant_address': data.get('plant_address', ''),
            'pin': data.get('pin', ''),
            'other': data.get('customer_other', '')
        }
        
        # 运输详情（可选）
        shipping_info = None
        if data.get('port_of_shipment') or data.get('country_of_origin') or data.get('port_of_destination'):
            shipping_info = {
                'port_of_shipment': data.get('port_of_shipment', ''),
                'country_of_origin': data.get('country_of_origin', ''),
                'port_of_destination': data.get('port_of_destination', ''),
                'place_of_destination': data.get('place_of_destination', ''),
                'shipment_term': data.get('shipment_term', '')
            }
        
        # 产品总体描述（可选）
        product_description = data.get('product_description', '')
        
        # 获取货币类型
        currency = data.get('currency', 'CNY').upper()
        
        # 发票信息
        invoice_info = {
            'number': data.get('invoice_number', ''),
            'date': data.get('invoice_date', datetime.now().strftime('%Y-%m-%d')),
            'po_number': data.get('po_number', '')
        }
        
        # 发票项目
        items = []
        item_count = int(data.get('item_count', 1))
        
        for i in range(item_count):
            description = data.get(f'item_description_{i}', '')
            if description:  # 只添加非空项目
                product_name = data.get(f'item_product_name_{i}', '')
                product_number = data.get(f'item_product_number_{i}', '')
                item_number = data.get(f'item_item_number_{i}', '')
                hs_code = data.get(f'item_hs_code_{i}', '')
                quantity = float(data.get(f'item_quantity_{i}', 0) or 0)
                unit_price = float(data.get(f'item_unit_price_{i}', 0) or 0)
                amount = float(data.get(f'item_amount_{i}', 0) or (quantity * unit_price))
                
                items.append({
                    'product_name': product_name,
                    'product_number': product_number,
                    'item_number': item_number,
                    'hs_code': hs_code,
                    'description': description,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'amount': amount
                })
        
        # 税费和折扣
        tax_rate = float(data.get('tax_rate', 0) or 0)
        discount = float(data.get('discount', 0) or 0)
        
        # 备注和支付信息
        notes = data.get('notes', '')
        payment_info = None
        if data.get('bank') or data.get('account'):
            payment_info = {
                'bank': data.get('bank', ''),
                'account': data.get('account', ''),
                'swift': data.get('swift', '')
            }
        
        # 生成唯一文件名
        filename = f"invoice_{invoice_info['number'] or uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # 生成发票
        try:
            create_invoice(
                output_path=output_path,
                company_info=company_info,
                customer_info=customer_info,
                invoice_info=invoice_info,
                items=items,
                tax_rate=tax_rate,
                discount=discount,
                notes=notes if notes else None,
                payment_info=payment_info,
                logo_path=logo_path,
                stamp_path=stamp_path,
                shipper_info=shipper_info,
                shipping_info=shipping_info,
                product_description=product_description if product_description else None,
                currency=currency
            )
        except Exception as e:
            # 如果生成失败，清理上传的文件
            if logo_path and os.path.exists(logo_path):
                try:
                    os.remove(logo_path)
                except:
                    pass
            if stamp_path and os.path.exists(stamp_path):
                try:
                    os.remove(stamp_path)
                except:
                    pass
            raise e
        
        # 清理上传的临时图片文件（在PDF生成成功后）
        if logo_path and os.path.exists(logo_path):
            try:
                os.remove(logo_path)
            except Exception as e:
                print(f"Warning: Could not remove logo file {logo_path}: {e}")
        if stamp_path and os.path.exists(stamp_path):
            try:
                os.remove(stamp_path)
            except Exception as e:
                print(f"Warning: Could not remove stamp file {stamp_path}: {e}")
        
        # 返回下载链接
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/download/{filename}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/download/<filename>')
def download_invoice(filename):
    """下载生成的发票PDF"""
    # 安全检查：防止路径遍历攻击
    if '..' in filename or '/' in filename or '\\' in filename:
        return "无效的文件名", 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    else:
        return "文件不存在", 404


@app.route('/preview', methods=['POST'])
def preview_invoice():
    """预览发票（返回JSON数据）"""
    try:
        data = request.form
        
        # 计算总计
        items = []
        subtotal = 0
        item_count = int(data.get('item_count', 1))
        
        for i in range(item_count):
            description = data.get(f'item_description_{i}', '')
            if description:
                quantity = float(data.get(f'item_quantity_{i}', 0) or 0)
                unit_price = float(data.get(f'item_unit_price_{i}', 0) or 0)
                amount = float(data.get(f'item_amount_{i}', 0) or (quantity * unit_price))
                subtotal += amount
                
                items.append({
                    'description': description,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'amount': amount
                })
        
        tax_rate = float(data.get('tax_rate', 0) or 0)
        discount = float(data.get('discount', 0) or 0)
        tax_amount = subtotal * (tax_rate / 100) if tax_rate > 0 else 0
        total = subtotal - discount + tax_amount
        
        return jsonify({
            'success': True,
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'discount': discount,
            'total': total,
            'items': items
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


if __name__ == '__main__':
    import sys
    import socket
    
    # 检查是否为生产环境
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    # 检查端口是否可用
    def is_port_available(port, host='0.0.0.0'):
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                result = s.bind((host, port))
                return True
        except OSError:
            return False
    
    # 获取服务器IP地址
    def get_server_ip():
        """获取服务器IP地址"""
        try:
            # 创建一个UDP socket来获取本机IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "无法获取"
    
    print("=" * 50)
    print("发票生成器 Web应用")
    print("=" * 50)
    
    # 检查端口
    if not is_port_available(port, host):
        print(f"❌ 错误: 端口 {port} 已被占用或无法绑定")
        print(f"请检查是否有其他进程在使用该端口")
        sys.exit(1)
    
    # 检查目录
    print(f"工作目录: {BASE_DIR}")
    print(f"模板目录: {os.path.join(BASE_DIR, 'templates')}")
    print(f"静态目录: {os.path.join(BASE_DIR, 'static')}")
    
    # 检查模板文件
    template_path = os.path.join(BASE_DIR, 'templates', 'index.html')
    if not os.path.exists(template_path):
        print(f"❌ 警告: 模板文件不存在: {template_path}")
    else:
        print(f"✅ 模板文件: {template_path}")
    
    # 检查静态文件
    static_path = os.path.join(BASE_DIR, 'static', 'css', 'style.css')
    if not os.path.exists(static_path):
        print(f"❌ 警告: 静态文件不存在: {static_path}")
    else:
        print(f"✅ 静态文件: {static_path}")
    
    print(f"运行模式: {'开发模式' if debug_mode else '生产模式'}")
    print(f"监听地址: {host}:{port}")
    print(f"本地访问: http://127.0.0.1:{port}")
    print(f"本地访问: http://localhost:{port}")
    
    if host == '0.0.0.0':
        server_ip = get_server_ip()
        print(f"外部访问: http://{server_ip}:{port}")
        print(f"外部访问: http://<服务器IP>:{port}")
    
    print(f"健康检查: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/health")
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)
    print("")
    print("💡 提示: 日志会显示在此终端")
    print("💡 如需后台运行: nohup python3 app.py > app.log 2>&1 &")
    print("💡 查看日志: tail -f app.log")
    print("")
    
    try:
        print(f"🚀 正在启动服务器...")
        app.run(debug=debug_mode, host=host, port=port, threaded=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

