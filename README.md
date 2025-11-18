# PDF发票生成器

一个功能完整的自动生成PDF格式发票的Python应用程序。

## 功能特性

- ✅ **Web界面** - 美观易用的网页前端，无需编程即可生成发票
- ✅ 自动生成专业的PDF格式发票
- ✅ 支持自定义公司信息、客户信息
- ✅ 支持多个发票项目（商品/服务），可动态添加/删除
- ✅ 实时计算小计、税费、折扣和总计
- ✅ 支持备注和支付信息
- ✅ 支持公司Logo和图章上传
- ✅ 美观的表格布局和样式
- ✅ 响应式设计，支持移动设备

## 安装

1. 确保已安装Python 3.7或更高版本

2. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 使用方法

### 🌐 方法1: Web界面（推荐）

这是最简单的方式，通过网页界面输入信息并生成发票：

1. 启动Web服务器：
```bash
python app.py
```

2. 在浏览器中打开：
```
http://127.0.0.1:5000
```

3. 填写表单信息：
   - 开票方信息（公司信息）
   - 收票方信息（客户信息）
   - 发票信息（发票号、日期等）
   - 发票项目（可添加多个项目）
   - 费用信息（税率、折扣）
   - 支付信息（可选）
   - 备注（可选）

4. 点击"生成PDF发票"按钮，系统会自动生成并下载PDF文件

**Web界面特性：**
- 📱 响应式设计，支持手机、平板、电脑
- ⚡ 实时计算总计金额
- ➕ 动态添加/删除发票项目
- 🎨 现代化的UI设计
- 💾 自动下载生成的PDF
- 🖼️ 支持上传公司Logo和图章

### 在代码中使用

```python
from invoice_generator import create_invoice

# 公司信息
company_info = {
    'name': '你的公司名称',
    'address': '公司地址',
    'phone': '联系电话',
    'email': '邮箱地址'
}

# 客户信息
customer_info = {
    'name': '客户名称',
    'address': '客户地址',
    'phone': '客户电话',
    'email': '客户邮箱'
}

# 发票信息
invoice_info = {
    'number': 'INV-2024-001',
    'date': '2024-12-01',
    'due_date': '2024-12-31'
}

# 发票项目
items = [
    {
        'description': '服务项目1',
        'quantity': 10,
        'unit_price': 100.00,
        'amount': 1000.00
    },
    {
        'description': '服务项目2',
        'quantity': 5,
        'unit_price': 200.00,
        'amount': 1000.00
    }
]

# 支付信息（可选）
payment_info = {
    'bank': '银行名称',
    'account': '账户号码',
    'swift': 'SWIFT代码'
}

# 生成发票
create_invoice(
    output_path='my_invoice.pdf',
    company_info=company_info,
    customer_info=customer_info,
    invoice_info=invoice_info,
    items=items,
    tax_rate=13.0,  # 税率（百分比）
    discount=100.0,  # 折扣金额
    notes='备注信息',
    payment_info=payment_info
)
```

## 项目结构

```
Project1/
├── app.py                # Flask Web应用主程序
├── invoice_generator.py  # 发票生成器核心类
├── requirements.txt      # Python依赖包
├── gunicorn_config.py    # Gunicorn生产环境配置
├── start_server.sh       # Linux/macOS启动脚本
├── start_server.bat      # Windows启动脚本
├── DEPLOYMENT.md         # 服务器部署指南
├── templates/            # HTML模板目录
│   └── index.html       # 发票表单页面
├── static/               # 静态文件目录
│   └── css/
│       └── style.css     # 样式文件
├── generated_invoices/   # 生成的PDF文件存储目录（自动创建）
└── README.md            # 说明文档
```

## 高级用法

### 使用InvoiceGenerator类

如果需要更精细的控制，可以直接使用 `InvoiceGenerator` 类：

```python
from invoice_generator import InvoiceGenerator

generator = InvoiceGenerator('output.pdf')
generator.add_header(company_info, invoice_info)
generator.add_customer_info(customer_info)
generator.add_items(items)
generator.add_total(subtotal, tax_rate, discount)
generator.add_footer(notes, payment_info)
generator.generate()
```

## 注意事项

1. 生成的PDF文件会保存在当前目录
2. 发票项目中的 `amount` 字段是可选的，如果不提供会自动计算为 `quantity * unit_price`
3. 税率和折扣都是可选的，默认为0
4. 备注和支付信息都是可选的

## 服务器部署

详细部署说明请参考 [DEPLOYMENT.md](DEPLOYMENT.md)

快速启动：
```bash
# Linux/macOS
./start_server.sh

# Windows
start_server.bat

# 或直接使用Python
python app.py
```

## 依赖包

- `reportlab`: PDF生成库
- `Pillow`: 图像处理库（reportlab的依赖）
- `Flask`: Web框架（用于Web界面）
- `gunicorn`: 生产环境WSGI服务器（可选）

## 许可证

MIT License

## 贡献

欢迎提交问题和改进建议！


