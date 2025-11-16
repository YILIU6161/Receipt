#!/usr/bin/env python3
"""
发票生成器主程序
使用示例和命令行接口
"""
from invoice_generator import create_invoice
from datetime import datetime, timedelta
import json
import sys
import os


def load_config(config_file: str = "config.json") -> dict:
    """
    从配置文件加载数据
    
    Args:
        config_file: 配置文件路径
    
    Returns:
        配置字典
    """
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_config(config: dict, config_file: str = "config.json"):
    """
    保存配置到文件
    
    Args:
        config: 配置字典
        config_file: 配置文件路径
    """
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def create_sample_invoice():
    """创建示例发票"""
    # 公司信息
    company_info = {
        'name': 'ABC科技有限公司',
        'address': '北京市朝阳区科技园区123号',
        'phone': '+86-10-12345678',
        'email': 'info@abctech.com'
    }
    
    # 客户信息
    customer_info = {
        'name': 'XYZ贸易有限公司',
        'address': '上海市浦东新区商业街456号',
        'phone': '+86-21-87654321',
        'email': 'contact@xyztrade.com'
    }
    
    # 发票信息
    today = datetime.now()
    invoice_info = {
        'number': f'INV-{today.strftime("%Y%m%d")}-001',
        'date': today.strftime('%Y-%m-%d'),
        'due_date': (today + timedelta(days=30)).strftime('%Y-%m-%d')
    }
    
    # 发票项目
    items = [
        {
            'description': '软件开发服务 - 网站开发',
            'quantity': 40,
            'unit_price': 500.00,
            'amount': 20000.00
        },
        {
            'description': '技术支持服务 - 月度维护',
            'quantity': 12,
            'unit_price': 1000.00,
            'amount': 12000.00
        },
        {
            'description': '咨询服务 - 技术咨询',
            'quantity': 8,
            'unit_price': 800.00,
            'amount': 6400.00
        }
    ]
    
    # 支付信息
    payment_info = {
        'bank': '中国工商银行',
        'account': '1234 5678 9012 3456',
        'swift': 'ICBKCNBJ'
    }
    
    # 生成发票
    output_file = f"invoice_{invoice_info['number']}.pdf"
    create_invoice(
        output_path=output_file,
        company_info=company_info,
        customer_info=customer_info,
        invoice_info=invoice_info,
        items=items,
        tax_rate=13.0,  # 13% 税率
        discount=500.0,  # 500元折扣
        notes='请于到期日期前付款。如有疑问，请联系我们。',
        payment_info=payment_info
    )
    
    print(f"\n示例发票已生成: {output_file}")
    return output_file


def create_invoice_from_config(config_file: str = "config.json", output_file: str = None):
    """
    从配置文件创建发票
    
    Args:
        config_file: 配置文件路径
        output_file: 输出文件路径（可选）
    """
    config = load_config(config_file)
    
    if not config:
        print(f"配置文件 {config_file} 不存在或为空，使用示例数据")
        return create_sample_invoice()
    
    # 从配置中提取信息
    company_info = config.get('company_info', {})
    customer_info = config.get('customer_info', {})
    invoice_info = config.get('invoice_info', {})
    items = config.get('items', [])
    tax_rate = config.get('tax_rate', 0.0)
    discount = config.get('discount', 0.0)
    notes = config.get('notes', '')
    payment_info = config.get('payment_info', {})
    
    # 如果没有指定输出文件，使用发票号
    if not output_file:
        invoice_number = invoice_info.get('number', 'invoice')
        output_file = f"invoice_{invoice_number}.pdf"
    
    create_invoice(
        output_path=output_file,
        company_info=company_info,
        customer_info=customer_info,
        invoice_info=invoice_info,
        items=items,
        tax_rate=tax_rate,
        discount=discount,
        notes=notes if notes else None,
        payment_info=payment_info if payment_info else None
    )
    
    print(f"\n发票已生成: {output_file}")
    return output_file


def create_sample_config():
    """创建示例配置文件"""
    today = datetime.now()
    config = {
        "company_info": {
            "name": "ABC科技有限公司",
            "address": "北京市朝阳区科技园区123号",
            "phone": "+86-10-12345678",
            "email": "info@abctech.com"
        },
        "customer_info": {
            "name": "XYZ贸易有限公司",
            "address": "上海市浦东新区商业街456号",
            "phone": "+86-21-87654321",
            "email": "contact@xyztrade.com"
        },
        "invoice_info": {
            "number": f"INV-{today.strftime('%Y%m%d')}-001",
            "date": today.strftime('%Y-%m-%d'),
            "due_date": (today + timedelta(days=30)).strftime('%Y-%m-%d')
        },
        "items": [
            {
                "description": "软件开发服务 - 网站开发",
                "quantity": 40,
                "unit_price": 500.00,
                "amount": 20000.00
            },
            {
                "description": "技术支持服务 - 月度维护",
                "quantity": 12,
                "unit_price": 1000.00,
                "amount": 12000.00
            }
        ],
        "tax_rate": 13.0,
        "discount": 500.0,
        "notes": "请于到期日期前付款。如有疑问，请联系我们。",
        "payment_info": {
            "bank": "中国工商银行",
            "account": "1234 5678 9012 3456",
            "swift": "ICBKCNBJ"
        }
    }
    
    save_config(config, "config.json")
    print("示例配置文件已创建: config.json")
    return config


def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "sample":
            # 生成示例发票
            create_sample_invoice()
        elif command == "config":
            # 创建示例配置文件
            create_sample_config()
        elif command == "generate":
            # 从配置文件生成发票
            config_file = sys.argv[2] if len(sys.argv) > 2 else "config.json"
            output_file = sys.argv[3] if len(sys.argv) > 3 else None
            create_invoice_from_config(config_file, output_file)
        else:
            print("用法:")
            print("  python main.py sample              - 生成示例发票")
            print("  python main.py config              - 创建示例配置文件")
            print("  python main.py generate [config]   - 从配置文件生成发票")
    else:
        # 默认生成示例发票
        print("生成示例发票...")
        create_sample_invoice()
        print("\n提示: 使用 'python main.py config' 创建配置文件")
        print("     使用 'python main.py generate' 从配置文件生成发票")


if __name__ == "__main__":
    main()


