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
from xml.sax.saxutils import escape
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
            rightMargin=1.0*cm,
            leftMargin=1.0*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        self.story = []
        self.styles = getSampleStyleSheet()
        self._total_amount = 0
        self._total_quantity = 0
        self.currency = 'CNY'  # 默认货币
        
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
        添加发票头部信息 - 按照图片风格：公司信息居中，然后是发票信息
        
        Args:
            company_info: 公司信息字典 {'name': '', 'address': '', 'phone': '', 'email': ''}
            invoice_info: 发票信息字典 {'number': '', 'date': '', 'po_number': ''}
            logo_path: 公司Logo图片路径（可选）
        """
        # 如果有Logo，先显示Logo（居中显示）
        if logo_path:
            try:
                # 尝试使用绝对路径
                if os.path.exists(logo_path):
                    abs_logo_path = os.path.abspath(logo_path)
                else:
                    # 如果相对路径不存在，尝试在当前目录查找
                    abs_logo_path = os.path.abspath(logo_path)
                    if not os.path.exists(abs_logo_path):
                        print(f"Warning: Logo file not found: {logo_path}")
                        logo_path = None
                
                if logo_path and os.path.exists(abs_logo_path):
                    logo_img = Image(abs_logo_path, width=3*cm, height=3*cm)
                    # 使用表格来居中显示logo
                    logo_table = Table([[logo_img]], colWidths=[16*cm])
                    logo_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ]))
                    self.story.append(logo_table)
                    self.story.append(Spacer(1, 0.2*cm))
            except Exception as e:
                print(f"Warning: Could not load logo image: {e}")
                print(f"Logo path: {logo_path}")
                import traceback
                traceback.print_exc()
        
        # 创建文本样式
        company_style = ParagraphStyle(
            'CompanyInfo',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=13,
            textColor=colors.black,
            alignment=1  # 居中
        )
        
        # 公司信息居中显示
        company_name = Paragraph(escape(company_info.get('name', '') or ''), company_style)
        company_address = Paragraph(escape(company_info.get('address', '') or ''), company_style)
        
        self.story.append(company_name)
        self.story.append(company_address)
        self.story.append(Spacer(1, 0.3*cm))
        
        # COMMERCIAL INVOICE 标题居中加粗
        title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.black,
            alignment=1,  # 居中
            spaceAfter=15
        )
        title = Paragraph("<b>COMMERCIAL INVOICE</b>", title_style)
        self.story.append(title)
        self.story.append(Spacer(1, 0.3*cm))
        
        # 发票信息：左右两列布局
        info_style = ParagraphStyle(
            'InfoText',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11,
            textColor=colors.black
        )
        
        # 左列：Invoice No. 和 Date
        invoice_left_data = [
            [Paragraph(f"Invoice No.: {escape(invoice_info.get('number', '') or '')}", info_style)],
            [Paragraph(f"Date: {escape(invoice_info.get('date', '') or '')}", info_style)],
        ]
        
        # 右列：Purchase Order No.
        invoice_right_data = [
            [Paragraph(f"Purchase Order No.: {escape(invoice_info.get('po_number', '') or '')}", info_style)],
            [Paragraph('', info_style)],  # 空行以保持对齐
        ]
        
        invoice_left_table = Table(invoice_left_data, colWidths=[8*cm])
        invoice_right_table = Table(invoice_right_data, colWidths=[8*cm])
        
        # 设置表格样式（无边框，无背景）
        for table in [invoice_left_table, invoice_right_table]:
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
        
        # 创建并排的两个表格
        invoice_info_table = Table([
            [invoice_left_table, invoice_right_table]
        ], colWidths=[8*cm, 8*cm])
        
        invoice_info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(invoice_info_table)
        self.story.append(Spacer(1, 0.4*cm))
    
    def add_shipper_and_consignee(self, shipper_info: Dict[str, str], customer_info: Dict[str, str]):
        """
        添加发货方和收货方信息 - 段落式布局，并排显示
        
        Args:
            shipper_info: 发货方信息字典 {'name': '', 'address': '', 'phone': ''}（必填）
            customer_info: 客户信息字典
        """
        # 创建段落样式，支持自动换行
        title_style = ParagraphStyle(
            'InfoTitle',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=12,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            spaceAfter=4
        )
        
        info_style = ParagraphStyle(
            'InfoText',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11,
            textColor=colors.black,
            leftIndent=0,
            rightIndent=0
        )
        
        # 构建发货方信息文本（左列）
        shipper_text_parts = ['<b>Shipper</b><br/>']
        shipper_name = shipper_info.get('name', '') or ''
        if shipper_name:
            shipper_text_parts.append(f"Shipper Name: {escape(shipper_name)}<br/>")
        shipper_address = shipper_info.get('address', '') or ''
        if shipper_address:
            shipper_text_parts.append(f"Shipper Address: {escape(shipper_address)}<br/>")
        shipper_phone = shipper_info.get('phone', '') or ''
        if shipper_phone:
            shipper_text_parts.append(f"Shipper Contact: {escape(shipper_phone)}")
        
        # 构建收货方信息文本（右列）
        customer_text_parts = ['<b>Consignee/Buyer</b><br/>']
        customer_name = customer_info.get('name', '') or ''
        if customer_name:
            customer_text_parts.append(f"Company Name: {escape(customer_name)}<br/>")
        
        plant_address = customer_info.get('plant_address', '')
        if plant_address:
            customer_text_parts.append(f"Plant Address: {escape(plant_address)}<br/>")
        
        pin = customer_info.get('pin', '')
        if pin:
            customer_text_parts.append(f"Pin: {escape(pin)}<br/>")
        
        address = customer_info.get('address', '')
        if address and not plant_address:
            customer_text_parts.append(f"Address: {escape(address)}<br/>")
        
        phone = customer_info.get('phone', '')
        if phone:
            customer_text_parts.append(f"Contact: {escape(phone)}<br/>")
        
        email = customer_info.get('email', '')
        if email:
            customer_text_parts.append(f"Other Information: {escape(email)}<br/>")
        
        other = customer_info.get('other', '')
        if other:
            customer_text_parts.append(f"Other: {escape(other)}")
        
        # 创建段落对象，设置宽度以支持自动换行
        shipper_para = Paragraph(''.join(shipper_text_parts), info_style)
        customer_para = Paragraph(''.join(customer_text_parts), info_style)
        
        # 使用表格进行并排布局（无边框，仅用于布局）
        layout_table = Table([
            [shipper_para, customer_para]
        ], colWidths=[8*cm, 8*cm])
        
        layout_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        self.story.append(layout_table)
        self.story.append(Spacer(1, 0.3*cm))
    
    def add_shipper_info(self, shipper_info: Dict[str, str]):
        """
        添加发货方信息 - 左列显示（保留以兼容旧代码）
        
        Args:
            shipper_info: 发货方信息字典 {'name': '', 'address': '', 'phone': ''}
        """
        info_style = ParagraphStyle(
            'InfoText',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11,
            textColor=colors.black
        )
        shipper_data = [
            [Paragraph('<b>Shipper</b>', info_style)],
            [Paragraph(escape(shipper_info.get('name', '') or ''), info_style)],
            [Paragraph(escape(shipper_info.get('address', '') or ''), info_style)],
            [Paragraph(escape(shipper_info.get('phone', '') or ''), info_style)],
        ]
        
        shipper_table = Table(shipper_data, colWidths=[8*cm])
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
    
    def add_customer_info(self, customer_info: Dict[str, str]):
        """
        添加收货方/买方信息
        
        Args:
            customer_info: 客户信息字典，包含所有字段
        """
        info_style = ParagraphStyle(
            'InfoText',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11,
            textColor=colors.black
        )
        customer_data = [
            [Paragraph('<b>Consignee/Buyer</b>', info_style)],
            [Paragraph(f"Company Name: {escape(customer_info.get('name', '') or '')}", info_style)],
        ]
        
        # 添加Plant Address
        plant_address = customer_info.get('plant_address', '')
        if plant_address:
            customer_data.append([Paragraph(f"Plant Address: {escape(plant_address)}", info_style)])
        
        # 添加Pin
        pin = customer_info.get('pin', '')
        if pin:
            customer_data.append([Paragraph(f"Pin: {escape(pin)}", info_style)])
        
        # 添加其他基本信息
        address = customer_info.get('address', '')
        if address and not plant_address:
            customer_data.append([Paragraph(f"Address: {escape(address)}", info_style)])
        
        phone = customer_info.get('phone', '')
        if phone:
            customer_data.append([Paragraph(f"Contact: {escape(phone)}", info_style)])
        
        email = customer_info.get('email', '')
        if email:
            customer_data.append([Paragraph(f"Other Information: {escape(email)}", info_style)])
        
        # 如果有其他内容，添加到列表中
        other = customer_info.get('other', '')
        if other:
            customer_data.append([Paragraph(f"Other: {escape(other)}", info_style)])
        
        customer_table = Table(customer_data, colWidths=[8*cm])
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
        
        # 将Shipper和Consignee/Buyer并排显示
        # 注意：这个方法需要在调用时配合使用
        self.story.append(customer_table)
    
    def add_shipping_details(self, shipping_info: Dict[str, str]):
        """
        添加运输详情 - 段落式布局，并排显示
        
        Args:
            shipping_info: 运输信息字典
        """
        info_style = ParagraphStyle(
            'InfoText',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11,
            textColor=colors.black
        )
        
        # 构建左列文本
        shipping_left_parts = ['<b>Shipping Details</b><br/>']
        
        port_of_shipment = shipping_info.get('port_of_shipment', '')
        if port_of_shipment:
            shipping_left_parts.append(f"Port of Shipment: {escape(port_of_shipment)}<br/>")
        
        country_of_origin = shipping_info.get('country_of_origin', '')
        if country_of_origin:
            shipping_left_parts.append(f"Country of Origin: {escape(country_of_origin)}")
        
        # 构建右列文本
        shipping_right_parts = ['<br/>']  # 空行以保持对齐
        
        port_of_destination = shipping_info.get('port_of_destination', '')
        if port_of_destination:
            shipping_right_parts.append(f"Port of Destination: {escape(port_of_destination)}<br/>")
        
        place_of_destination = shipping_info.get('place_of_destination', '')
        if place_of_destination:
            shipping_right_parts.append(f"Place of Final Destination: {escape(place_of_destination)}<br/>")
        
        shipment_term = shipping_info.get('shipment_term', '')
        if shipment_term:
            shipping_right_parts.append(f"Shipment Term: {escape(shipment_term)}")
        
        # 如果有内容才显示
        if len(shipping_left_parts) > 1 or len(shipping_right_parts) > 1:
            shipping_left_para = Paragraph(''.join(shipping_left_parts), info_style)
            shipping_right_para = Paragraph(''.join(shipping_right_parts), info_style)
            
            # 使用表格进行并排布局（无边框，仅用于布局）
            layout_table = Table([
                [shipping_left_para, shipping_right_para]
            ], colWidths=[8*cm, 8*cm])
            
            layout_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            
            self.story.append(layout_table)
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
        # 添加 "Product Information" 标题（居中加粗）
        title_style = ParagraphStyle(
            'ProductInfoTitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.black,
            alignment=1,  # 居中
            spaceAfter=8
        )
        title = Paragraph("<b>Product Information</b>", title_style)
        self.story.append(title)
        
        # 如果有产品总体描述，添加在标题下方
        if product_description:
            desc_style = ParagraphStyle(
                'ProductDescription',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#333333'),
                spaceAfter=8
            )
            desc_para = Paragraph(f"Product Description: {product_description}", desc_style)
            self.story.append(desc_para)
            self.story.append(Spacer(1, 0.2*cm))
        
        # 创建文本样式用于表格单元格
        cell_style = ParagraphStyle(
            'TableCell',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.black
        )
        
        # 创建单行文本样式（用于不允许换行的列）
        single_line_style = ParagraphStyle(
            'SingleLineCell',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.black,
            wordWrap='CJK'  # 允许 CJK 字符换行，但尽量保持单行
        )
        
        # 表头 - 添加Product Name列，金额相关列显示货币单位
        # 表头内容加粗并居中显示
        currency_label = self.currency if hasattr(self, 'currency') else 'CNY'
        table_data = [[
            Paragraph('<b>No.</b>', cell_style),
            Paragraph('<b>Product Name</b>', cell_style),
            Paragraph('<b>Product Number</b>', cell_style),
            Paragraph('<b>Item Number</b>', cell_style),
            Paragraph('<b>HS Code</b>', cell_style),
            Paragraph('<b>Quantity</b>', cell_style),
            Paragraph(f'<b>Unit Price ({currency_label})</b>', cell_style),
            Paragraph(f'<b>Amount ({currency_label})</b>', cell_style)
        ]]
        
        # 添加项目数据
        total_amount = 0
        total_quantity = 0
        for idx, item in enumerate(items, 1):
            product_name = item.get('product_name', '') or ''
            product_number = item.get('product_number', '') or ''
            item_number = item.get('item_number', '') or ''
            hs_code = item.get('hs_code', '') or ''
            description = item.get('description', '') or ''
            # 如果没有product_name，使用description
            if not product_name:
                product_name = description
            quantity = item.get('quantity', 0)
            unit_price = item.get('unit_price', 0)
            amount = item.get('amount', quantity * unit_price)
            total_amount += amount
            total_quantity += quantity
            
            # 转义HTML特殊字符并创建Paragraph对象
            # Product Name 允许换行，其他列使用单行样式以确保在一行显示
            # 所有项目内容普通显示（不加粗，无下划线）
            table_data.append([
                Paragraph(str(idx), single_line_style),
                Paragraph(f"{escape(product_name)}", cell_style),  # Product Name 允许换行
                Paragraph(f"{escape(product_number)}", single_line_style),
                Paragraph(f"{escape(item_number)}", single_line_style),
                Paragraph(f"{escape(hs_code)}", single_line_style),
                Paragraph(f"{quantity:.0f}", single_line_style),
                Paragraph(f"{unit_price:.2f}", single_line_style),
                Paragraph(f"{amount:,.2f}", single_line_style)
            ])
        
        # 创建表格 - 调整列宽以适应新列（包含Product Name）
        # A4宽度21cm，减去左右边距2cm，可用宽度19cm
        # 列宽分配：No.(0.7) + Product Name(4.5) + Product No.(3.0) + Item No.(3.0) + HS Code(2.0) + Quantity(1.2) + Unit Price(2.0) + Amount(2.6) = 19cm
        # Product Name 允许换行，其他列增加宽度以确保单行显示
        items_table = Table(
            table_data,
            colWidths=[0.7*cm, 4.5*cm, 3.0*cm, 3.0*cm, 2.0*cm, 1.2*cm, 2.0*cm, 2.6*cm]
        )
        
        # 设置表格样式
        items_table.setStyle(TableStyle([
            # 表头样式
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            
            # 数据行样式
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # 改为TOP以便多行文本正确显示
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),  # 所有数据列居中
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))
        
        # 按照图片风格：在表格底部添加总计行
        # 计算总计（包含税费和折扣）
        tax_amount = 0  # 税费在add_total中计算
        total = total_amount  # 暂时使用总金额，实际会在add_total中计算
        
        # 添加总计行到表格数据中（去掉货币单位）
        if total_quantity > 0:
            table_data.append([
                Paragraph('', cell_style),
                Paragraph('<b>TOTAL</b>', cell_style),
                Paragraph('', cell_style),
                Paragraph('', cell_style),
                Paragraph('', cell_style),
                Paragraph(f"<b>{total_quantity:.0f}</b>", cell_style),
                Paragraph('', cell_style),
                Paragraph(f"<b>{total_amount:,.2f}</b>", cell_style)
            ])
        else:
            table_data.append([
                Paragraph('', cell_style),
                Paragraph('<b>TOTAL</b>', cell_style),
                Paragraph('', cell_style),
                Paragraph('', cell_style),
                Paragraph('', cell_style),
                Paragraph('', cell_style),
                Paragraph('', cell_style),
                Paragraph(f"<b>{total_amount:,.2f}</b>", cell_style)
            ])
        
        # 重新创建包含总计行的表格
        items_table = Table(
            table_data,
            colWidths=[0.7*cm, 4.5*cm, 3.0*cm, 3.0*cm, 2.0*cm, 1.2*cm, 2.0*cm, 2.6*cm]
        )
        
        # 设置表格样式（包括总计行）
        total_row_idx = len(table_data) - 1
        items_table.setStyle(TableStyle([
            # 表头样式 - 白色背景，黑色文字
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            
            # 数据行样式
            ('BACKGROUND', (0, 1), (-1, total_row_idx-1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, total_row_idx-1), colors.black),
            ('FONTNAME', (0, 1), (-1, total_row_idx-1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, total_row_idx-1), 8),
            
            # 总计行样式
            ('BACKGROUND', (0, total_row_idx), (-1, total_row_idx), colors.white),
            ('FONTNAME', (0, total_row_idx), (-1, total_row_idx), 'Helvetica-Bold'),
            ('FONTSIZE', (1, total_row_idx), (1, total_row_idx), 9),  # TOTAL 字体稍大
            ('FONTSIZE', (5, total_row_idx), (5, total_row_idx), 9),  # 数量字体
            ('FONTSIZE', (7, total_row_idx), (7, total_row_idx), 9),  # 金额字体
            
            # 边框
            ('GRID', (0, 0), (-1, total_row_idx), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 1), (-1, total_row_idx-1), 'CENTER'),  # 所有数据列居中
            ('ALIGN', (1, total_row_idx), (1, total_row_idx), 'LEFT'),  # TOTAL 左对齐
            ('ALIGN', (0, total_row_idx), (0, total_row_idx), 'CENTER'),  # 总计行其他列居中
            ('ALIGN', (2, total_row_idx), (4, total_row_idx), 'CENTER'),  # 总计行其他列居中
            ('ALIGN', (5, total_row_idx), (5, total_row_idx), 'CENTER'),  # 总数量居中
            ('ALIGN', (6, total_row_idx), (7, total_row_idx), 'CENTER'),  # 总金额居中
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))
        
        self.story.append(items_table)
        self.story.append(Spacer(1, 0.3*cm))
        
        # 保存总金额和总数量，供add_total使用
        self._total_amount = total_amount
        self._total_quantity = total_quantity
    
    def add_total(self, subtotal: float, tax_rate: float = 0.0, discount: float = 0.0, total_quantity: float = 0.0):
        """
        添加总计信息（如果税费或折扣不为0）
        
        Args:
            subtotal: 小计金额
            tax_rate: 税率（百分比，如 13 表示 13%）
            discount: 折扣金额
            total_quantity: 总数量（已显示在表格中，这里不再显示）
        """
        # 如果税费和折扣都为0，则不显示额外的总计信息
        if tax_rate == 0 and discount == 0:
            return
        
        tax_amount = subtotal * (tax_rate / 100) if tax_rate > 0 else 0
        total = subtotal - discount + tax_amount
        
        # 创建文本样式
        cell_style = ParagraphStyle(
            'TableCell',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.black
        )
        
        total_data = []
        # 根据货币类型显示标签
        currency_label = self.currency if hasattr(self, 'currency') else 'CNY'
        total_data.extend([
            ['', '', '', '', '', '', f'Subtotal ({currency_label}):', f"{subtotal:,.2f}"],
            ['', '', '', '', '', '', f'Discount ({currency_label}):', f"-{discount:,.2f}"],
            ['', '', '', '', '', '', f'Tax ({currency_label}):', f"{tax_amount:,.2f}"],
            ['', '', '', '', '', '', f'<b>Total Amount ({currency_label}):</b>', f"<b>{total:,.2f}</b>"],
        ])
        
        total_table = Table(
            total_data,
            colWidths=[0.7*cm, 4.5*cm, 3.0*cm, 3.0*cm, 2.0*cm, 1.2*cm, 2.0*cm, 2.6*cm]
        )
        
        total_table.setStyle(TableStyle([
            ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),  # 金额列右对齐
            ('FONTNAME', (6, 0), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (6, 0), (-1, -2), 10),
            ('FONTNAME', (6, 3), (-1, 3), 'Helvetica-Bold'),
            ('FONTSIZE', (6, 3), (-1, 3), 11),
            ('TEXTCOLOR', (6, 3), (-1, 3), colors.HexColor('#d32f2f')),
            ('LINEABOVE', (6, 0), (-1, 0), 1, colors.grey),
            ('LINEBELOW', (6, 3), (-1, 3), 2, colors.HexColor('#d32f2f')),
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
    shipper_info: Dict[str, str],
    tax_rate: float = 0.0,
    discount: float = 0.0,
    notes: Optional[str] = None,
    payment_info: Optional[Dict[str, str]] = None,
    logo_path: Optional[str] = None,
    stamp_path: Optional[str] = None,
    shipping_info: Optional[Dict[str, str]] = None,
    product_description: Optional[str] = None,
    currency: str = 'CNY'
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
        shipper_info: 发货方信息（必填）
        shipping_info: 运输详情（可选）
        product_description: 产品总体描述（可选）
    
    Returns:
        生成的PDF文件路径
    """
    generator = InvoiceGenerator(output_path)
    generator.currency = currency.upper()  # 保存货币类型
    generator.add_header(company_info, invoice_info, logo_path)
    
    # 添加发货方和收货方信息（并排显示）
    generator.add_shipper_and_consignee(shipper_info, customer_info)
    
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


