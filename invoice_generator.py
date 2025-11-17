"""
发票生成器 - 自动生成PDF格式发票
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from typing import List, Dict, Optional
import os


class InvoiceGenerator:
    """PDF发票生成器类"""
    
    def __init__(self, output_path: str = "invoice.pdf"):
        """
        初始化发票生成器
        
        Args:
            output_path: 输出PDF文件路径
        """
        self.output_path = output_path
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        self.story = []
        self.styles = getSampleStyleSheet()
        
        # 注册中文字体（如果系统有的话）
        self._setup_fonts()
    
    def _setup_fonts(self):
        """设置字体支持中文"""
        try:
            # 尝试注册中文字体（需要系统有相应字体文件）
            # 这里使用默认字体，如果需要中文支持，可以添加字体文件
            pass
        except:
            pass
    
    def add_header(self, company_info: Dict[str, str], invoice_info: Dict[str, str], logo_path: Optional[str] = None):
        """
        添加发票头部信息
        
        Args:
            company_info: 公司信息字典 {'name': '', 'address': '', 'phone': '', 'email': ''}
            invoice_info: 发票信息字典 {'number': '', 'date': '', 'due_date': ''}
            logo_path: 公司Logo图片路径（可选）
        """
        # 如果有Logo，创建带Logo的头部
        if logo_path and os.path.exists(logo_path):
            try:
                # 使用绝对路径确保能找到文件
                abs_logo_path = os.path.abspath(logo_path)
                if not os.path.exists(abs_logo_path):
                    raise FileNotFoundError(f"Logo file not found: {abs_logo_path}")
                
                logo_img = Image(abs_logo_path, width=3*cm, height=3*cm)
                logo_img.hAlign = 'LEFT'
                
                # 创建Logo和标题的布局
                header_data = [
                    [logo_img, Paragraph("COMMERCIAL INVOICE", ParagraphStyle(
                        'CustomTitle',
                        parent=self.styles['Heading1'],
                        fontSize=20,
                        textColor=colors.HexColor('#1a1a1a'),
                        alignment=1  # 居中
                    ))]
                ]
                header_table = Table(header_data, colWidths=[4*cm, 12*cm])
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ]))
                self.story.append(header_table)
            except Exception as e:
                print(f"Warning: Could not load logo image: {e}")
                print(f"Logo path: {logo_path}")
                # 如果Logo加载失败，使用默认标题
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=self.styles['Heading1'],
                    fontSize=20,
                    textColor=colors.HexColor('#1a1a1a'),
                    spaceAfter=20,
                    alignment=1  # 居中
                )
                title = Paragraph("COMMERCIAL INVOICE", title_style)
                self.story.append(title)
        else:
            # 没有Logo时使用默认标题
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=1  # 居中
            )
            title = Paragraph("INVOICE", title_style)
            self.story.append(title)
        
        self.story.append(Spacer(1, 0.3*cm))
        
        # 创建两列布局：Issuer信息和发票信息
        issuer_data = [
            ['<b>Issuer</b>'],
            [f"{company_info.get('name', '')}"],
            [f"{company_info.get('address', '')}"],
            [f"{company_info.get('phone', '')}"],
        ]
        
        invoice_data = [
            ['<b>Invoice Information</b>'],
            [f"Invoice No.: {invoice_info.get('number', '')}"],
            [f"Date: {invoice_info.get('date', '')}"],
            [f"Purchase Order No.: {invoice_info.get('po_number', '')}"],
        ]
        
        # 创建表格
        issuer_table = Table(issuer_data, colWidths=[8*cm])
        invoice_table = Table(invoice_data, colWidths=[8*cm])
        
        # 设置表格样式
        issuer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        invoice_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        # 创建并排的两个表格
        combined_table = Table([
            [issuer_table, invoice_table]
        ], colWidths=[8*cm, 8*cm])
        
        combined_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(combined_table)
        self.story.append(Spacer(1, 0.5*cm))
    
    def add_shipper_info(self, shipper_info: Dict[str, str]):
        """
        添加发货方信息
        
        Args:
            shipper_info: 发货方信息字典 {'name': '', 'address': '', 'phone': ''}
        """
        shipper_data = [
            ['<b>Shipper</b>'],
            [f"{shipper_info.get('name', '')}"],
            [f"{shipper_info.get('address', '')}"],
            [f"{shipper_info.get('phone', '')}"],
        ]
        
        shipper_table = Table(shipper_data, colWidths=[16*cm])
        shipper_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8e8e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(shipper_table)
        self.story.append(Spacer(1, 0.3*cm))
    
    def add_customer_info(self, customer_info: Dict[str, str]):
        """
        添加收货方/买方信息
        
        Args:
            customer_info: 客户信息字典，包含所有字段
        """
        customer_data = [
            ['<b>Consignee/Buyer</b>'],
            [f"Company Name: {customer_info.get('name', '')}"],
        ]
        
        # 添加Plant Address
        plant_address = customer_info.get('plant_address', '')
        if plant_address:
            customer_data.append([f"Plant Address: {plant_address}"])
        
        # 添加Pin
        pin = customer_info.get('pin', '')
        if pin:
            customer_data.append([f"Pin: {pin}"])
        
        # 添加State Code
        state_code = customer_info.get('state_code', '')
        if state_code:
            customer_data.append([f"CHAKAN State Code: {state_code}"])
        
        # 添加Registered Office Address
        registered_address = customer_info.get('registered_address', '')
        if registered_address:
            customer_data.append([f"Registered Office Address: {registered_address}"])
        
        # 添加PAN NO.
        pan_no = customer_info.get('pan_no', '')
        if pan_no:
            customer_data.append([f"Company PAN NO.: {pan_no}"])
        
        # 添加GST NO.
        gst_no = customer_info.get('gst_no', '')
        if gst_no:
            customer_data.append([f"Company GST NO.MAHARASHTRA: {gst_no}"])
        
        # 添加IEC No.
        iec_no = customer_info.get('iec_no', '')
        if iec_no:
            customer_data.append([f"IEC No.: {iec_no}"])
        
        # 添加其他基本信息
        address = customer_info.get('address', '')
        if address and not plant_address:
            customer_data.append([f"Address: {address}"])
        
        phone = customer_info.get('phone', '')
        if phone:
            customer_data.append([f"Phone: {phone}"])
        
        email = customer_info.get('email', '')
        if email:
            customer_data.append([f"Email: {email}"])
        
        # 如果有其他内容，添加到列表中
        other = customer_info.get('other', '')
        if other:
            customer_data.append([f"Other: {other}"])
        
        customer_table = Table(customer_data, colWidths=[16*cm])
        customer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8e8e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(customer_table)
        self.story.append(Spacer(1, 0.3*cm))
    
    def add_shipping_details(self, shipping_info: Dict[str, str]):
        """
        添加运输详情
        
        Args:
            shipping_info: 运输信息字典
        """
        shipping_data = [
            ['<b>Shipping Details</b>'],
        ]
        
        port_of_shipment = shipping_info.get('port_of_shipment', '')
        if port_of_shipment:
            shipping_data.append([f"Port of Shipment: {port_of_shipment}"])
        
        country_of_origin = shipping_info.get('country_of_origin', '')
        if country_of_origin:
            shipping_data.append([f"Country of Origin: {country_of_origin}"])
        
        port_of_destination = shipping_info.get('port_of_destination', '')
        if port_of_destination:
            shipping_data.append([f"Port of Destination: {port_of_destination}"])
        
        place_of_destination = shipping_info.get('place_of_destination', '')
        if place_of_destination:
            shipping_data.append([f"Place of Final Destination: {place_of_destination}"])
        
        shipment_term = shipping_info.get('shipment_term', '')
        if shipment_term:
            shipping_data.append([f"Shipment Term: {shipment_term}"])
        
        if len(shipping_data) > 1:  # 如果有内容才显示
            shipping_table = Table(shipping_data, colWidths=[16*cm])
            shipping_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8e8e8')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            self.story.append(shipping_table)
            self.story.append(Spacer(1, 0.3*cm))
    
    def add_items(self, items: List[Dict[str, any]], product_description: Optional[str] = None):
        """
        添加发票项目列表
        
        Args:
            items: 项目列表，每个项目包含 {
                'product_name': '', 'product_number': '', 'item_number': '', 'hs_code': '', 
                'description': '', 'quantity': 0, 'unit_price': 0, 'amount': 0
            }
            product_description: 产品总体描述（可选）
        """
        # 如果有产品总体描述，先添加
        if product_description:
            desc_style = ParagraphStyle(
                'ProductDescription',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#333333'),
                spaceAfter=8
            )
            desc_para = Paragraph(f"<b>Product Description (overall):</b> {product_description}", desc_style)
            self.story.append(desc_para)
            self.story.append(Spacer(1, 0.2*cm))
        
        # 表头 - 添加Product Name列
        table_data = [['No.', 'Product Name', 'Product Number', 'Item Number', 'HS Code', 'Quantity', 'Unit Price (CNY)', 'Amount (CNY)']]
        
        # 添加项目数据
        total_amount = 0
        total_quantity = 0
        for idx, item in enumerate(items, 1):
            product_name = item.get('product_name', '')
            product_number = item.get('product_number', '')
            item_number = item.get('item_number', '')
            hs_code = item.get('hs_code', '')
            description = item.get('description', '')
            # 如果没有product_name，使用description
            if not product_name:
                product_name = description
            quantity = item.get('quantity', 0)
            unit_price = item.get('unit_price', 0)
            amount = item.get('amount', quantity * unit_price)
            total_amount += amount
            total_quantity += quantity
            
            table_data.append([
                str(idx),
                product_name,
                product_number,
                item_number,
                hs_code,
                f"{quantity:.0f}",
                f"CNY {unit_price:.2f}",
                f"CNY {amount:,.2f}"
            ])
        
        # 创建表格 - 调整列宽以适应新列（包含Product Name）
        # A4宽度21cm，减去左右边距3cm，可用宽度18cm
        # 列宽分配：No.(0.6) + Product Name(2.5) + Product No.(1.2) + Item No.(1.2) + HS Code(1.2) + Quantity(0.9) + Unit Price(1.3) + Amount(1.3) = 11.2cm
        items_table = Table(
            table_data,
            colWidths=[0.6*cm, 2.5*cm, 1.2*cm, 1.2*cm, 1.2*cm, 0.9*cm, 1.3*cm, 1.3*cm]
        )
        
        # 设置表格样式
        items_table.setStyle(TableStyle([
            # 表头样式
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            
            # 数据行样式
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (4, -1), 'LEFT'),  # Product Name, Product Number, Item Number, HS Code 左对齐
            ('ALIGN', (5, 1), (5, -1), 'CENTER'),  # Quantity 居中
            ('ALIGN', (6, 1), (7, -1), 'RIGHT'),  # Unit Price, Amount 右对齐
        ]))
        
        self.story.append(items_table)
        self.story.append(Spacer(1, 0.3*cm))
        
        # 添加总计（包含总数量）
        self.add_total(total_amount, total_quantity=total_quantity)
    
    def add_total(self, subtotal: float, tax_rate: float = 0.0, discount: float = 0.0, total_quantity: float = 0.0):
        """
        添加总计信息
        
        Args:
            subtotal: 小计金额
            tax_rate: 税率（百分比，如 13 表示 13%）
            discount: 折扣金额
            total_quantity: 总数量
        """
        tax_amount = subtotal * (tax_rate / 100) if tax_rate > 0 else 0
        total = subtotal - discount + tax_amount
        
        total_data = []
        
        # 如果有总数量，先显示总数量
        if total_quantity > 0:
            total_data.append(['', '', '', '', '', f"<b>Total Quantity:</b> {total_quantity:.0f}", '', ''])
        
        total_data.extend([
            ['', '', '', '', '', '', 'Subtotal:', f"CNY {subtotal:,.2f}"],
            ['', '', '', '', '', '', 'Discount:', f"-CNY {discount:,.2f}"],
            ['', '', '', '', '', '', 'Tax:', f"CNY {tax_amount:,.2f}"],
            ['', '', '', '', '', '', '<b>Total Amount (CNY):</b>', f"<b>CNY {total:,.2f}</b>"],
        ])
        
        total_table = Table(
            total_data,
            colWidths=[0.6*cm, 2.5*cm, 1.2*cm, 1.2*cm, 1.2*cm, 0.9*cm, 1.3*cm, 1.3*cm]
        )
        
        total_table.setStyle(TableStyle([
            ('ALIGN', (5, 0), (5, 0), 'RIGHT'),  # Total Quantity 右对齐
            ('ALIGN', (6, 1), (-1, -1), 'RIGHT'),  # 金额列右对齐
            ('FONTNAME', (6, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (6, 1), (-1, -2), 10),
            ('FONTNAME', (5, 0), (5, 0), 'Helvetica-Bold'),
            ('FONTNAME', (6, 4), (-1, 4), 'Helvetica-Bold'),
            ('FONTSIZE', (6, 4), (-1, 4), 11),
            ('TEXTCOLOR', (6, 4), (-1, 4), colors.HexColor('#d32f2f')),
            ('LINEABOVE', (6, 1), (-1, 1), 1, colors.grey),
            ('LINEBELOW', (6, 4), (-1, 4), 2, colors.HexColor('#d32f2f')),
        ]))
        
        self.story.append(total_table)
        self.story.append(Spacer(1, 0.3*cm))
    
    def add_footer(self, notes: Optional[str] = None, payment_info: Optional[Dict[str, str]] = None, stamp_path: Optional[str] = None):
        """
        添加发票底部信息
        
        Args:
            notes: 备注信息
            payment_info: 支付信息字典 {'bank': '', 'account': '', 'swift': ''}
            stamp_path: 图章图片路径（可选）
        """
        # 创建底部内容表格，包含备注、支付信息和图章
        footer_rows = []
        
        # 备注和支付信息（左侧）
        left_content = []
        if notes:
            left_content.append(f"<b>Notes:</b> {notes}")
        if payment_info:
            left_content.append(f"<b>Payment Information:</b>")
            left_content.append(f"Bank: {payment_info.get('bank', '')}")
            left_content.append(f"Account: {payment_info.get('account', '')}")
            if payment_info.get('swift'):
                left_content.append(f"SWIFT: {payment_info.get('swift', '')}")
        
        # 图章（右侧）
        right_content = None
        if stamp_path and os.path.exists(stamp_path):
            try:
                abs_stamp_path = os.path.abspath(stamp_path)
                if os.path.exists(abs_stamp_path):
                    stamp_img = Image(abs_stamp_path, width=2.5*cm, height=2.5*cm)
                    right_content = stamp_img
            except Exception as e:
                print(f"Warning: Could not load stamp image: {e}")
        
        # 创建底部布局
        if left_content or right_content:
            if left_content:
                left_text = '<br/>'.join(left_content)
                left_para = Paragraph(left_text, ParagraphStyle(
                    'Footer',
                    parent=self.styles['Normal'],
                    fontSize=9,
                    textColor=colors.HexColor('#666666'),
                    leading=11
                ))
            else:
                left_para = Paragraph('', ParagraphStyle('Footer', parent=self.styles['Normal']))
            
            if right_content:
                # 有图章时，左右布局
                footer_data = [[left_para, right_content]]
                footer_table = Table(footer_data, colWidths=[12*cm, 4*cm])
                footer_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ]))
            else:
                # 没有图章时，只有左侧内容
                footer_data = [[left_para]]
                footer_table = Table(footer_data, colWidths=[16*cm])
                footer_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ]))
            
            self.story.append(Spacer(1, 0.3*cm))
            self.story.append(footer_table)
    
    def generate(self):
        """生成PDF发票"""
        self.doc.build(self.story)
        print(f"发票已成功生成: {self.output_path}")


def create_invoice(
    output_path: str,
    company_info: Dict[str, str],
    customer_info: Dict[str, str],
    invoice_info: Dict[str, str],
    items: List[Dict[str, any]],
    tax_rate: float = 0.0,
    discount: float = 0.0,
    notes: Optional[str] = None,
    payment_info: Optional[Dict[str, str]] = None,
    logo_path: Optional[str] = None,
    stamp_path: Optional[str] = None,
    shipper_info: Optional[Dict[str, str]] = None,
    shipping_info: Optional[Dict[str, str]] = None,
    product_description: Optional[str] = None
) -> str:
    """
    创建发票的便捷函数
    
    Args:
        output_path: 输出PDF文件路径
        company_info: 公司信息（Issuer）
        customer_info: 客户信息（Consignee/Buyer）
        invoice_info: 发票信息（包含 po_number）
        items: 项目列表（包含 product_name）
        tax_rate: 税率（百分比）
        discount: 折扣金额
        notes: 备注
        payment_info: 支付信息
        logo_path: 公司Logo图片路径（可选）
        stamp_path: 图章图片路径（可选）
        shipper_info: 发货方信息（可选）
        shipping_info: 运输详情（可选）
        product_description: 产品总体描述（可选）
    
    Returns:
        生成的PDF文件路径
    """
    generator = InvoiceGenerator(output_path)
    generator.add_header(company_info, invoice_info, logo_path)
    
    # 添加发货方信息
    if shipper_info:
        generator.add_shipper_info(shipper_info)
    
    # 添加收货方/买方信息
    generator.add_customer_info(customer_info)
    
    # 添加运输详情
    if shipping_info:
        generator.add_shipping_details(shipping_info)
    
    # 添加产品项目和描述
    generator.add_items(items, product_description=product_description)
    
    # 计算小计和总数量
    subtotal = sum(item.get('amount', item.get('quantity', 0) * item.get('unit_price', 0)) 
                   for item in items)
    total_quantity = sum(item.get('quantity', 0) for item in items)
    
    generator.add_total(subtotal, tax_rate, discount, total_quantity=total_quantity)
    generator.add_footer(notes, payment_info, stamp_path)
    generator.generate()
    
    return output_path


