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
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
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
                
                logo_img = Image(abs_logo_path, width=4*cm, height=4*cm)
                logo_img.hAlign = 'LEFT'
                
                # 创建Logo和标题的布局
                header_data = [
                    [logo_img, Paragraph("INVOICE", ParagraphStyle(
                        'CustomTitle',
                        parent=self.styles['Heading1'],
                        fontSize=24,
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
                    fontSize=24,
                    textColor=colors.HexColor('#1a1a1a'),
                    spaceAfter=30,
                    alignment=1  # 居中
                )
                title = Paragraph("INVOICE", title_style)
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
        
        self.story.append(Spacer(1, 0.5*cm))
        
        # 创建两列布局：公司信息和发票信息
        company_data = [
            ['<b>Bill From</b>'],
            [f"Company Name: {company_info.get('name', '')}"],
            [f"Address: {company_info.get('address', '')}"],
            [f"Phone: {company_info.get('phone', '')}"],
            [f"Email: {company_info.get('email', '')}"],
        ]
        
        invoice_data = [
            ['<b>Invoice Information</b>'],
            [f"Invoice Number: {invoice_info.get('number', '')}"],
            [f"Invoice Date: {invoice_info.get('date', '')}"],
            [f"Due Date: {invoice_info.get('due_date', '')}"],
        ]
        
        # 创建表格
        company_table = Table(company_data, colWidths=[8*cm])
        invoice_table = Table(invoice_data, colWidths=[8*cm])
        
        # 设置表格样式
        company_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        invoice_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        # 创建并排的两个表格
        combined_table = Table([
            [company_table, invoice_table]
        ], colWidths=[8*cm, 8*cm])
        
        combined_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(combined_table)
        self.story.append(Spacer(1, 1*cm))
    
    def add_customer_info(self, customer_info: Dict[str, str]):
        """
        添加客户信息
        
        Args:
            customer_info: 客户信息字典 {'name': '', 'address': '', 'phone': '', 'email': ''}
        """
        customer_data = [
            ['<b>Bill To</b>'],
            [f"Customer Name: {customer_info.get('name', '')}"],
            [f"Address: {customer_info.get('address', '')}"],
            [f"Phone: {customer_info.get('phone', '')}"],
            [f"Email: {customer_info.get('email', '')}"],
        ]
        
        customer_table = Table(customer_data, colWidths=[16*cm])
        customer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8e8e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(customer_table)
        self.story.append(Spacer(1, 1*cm))
    
    def add_items(self, items: List[Dict[str, any]]):
        """
        添加发票项目列表
        
        Args:
            items: 项目列表，每个项目包含 {'description': '', 'quantity': 0, 'unit_price': 0, 'amount': 0}
        """
        # 表头
        table_data = [['No.', 'Description', 'Quantity', 'Unit Price', 'Amount']]
        
        # 添加项目数据
        total_amount = 0
        for idx, item in enumerate(items, 1):
            description = item.get('description', '')
            quantity = item.get('quantity', 0)
            unit_price = item.get('unit_price', 0)
            amount = item.get('amount', quantity * unit_price)
            total_amount += amount
            
            table_data.append([
                str(idx),
                description,
                f"{quantity:.2f}",
                f"${unit_price:.2f}",
                f"${amount:.2f}"
            ])
        
        # 创建表格
        items_table = Table(
            table_data,
            colWidths=[1.5*cm, 8*cm, 2*cm, 2.5*cm, 2*cm]
        )
        
        # 设置表格样式
        items_table.setStyle(TableStyle([
            # 表头样式
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # 数据行样式
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # 描述左对齐
        ]))
        
        self.story.append(items_table)
        self.story.append(Spacer(1, 0.5*cm))
        
        # 添加总计
        self.add_total(total_amount)
    
    def add_total(self, subtotal: float, tax_rate: float = 0.0, discount: float = 0.0):
        """
        添加总计信息
        
        Args:
            subtotal: 小计金额
            tax_rate: 税率（百分比，如 13 表示 13%）
            discount: 折扣金额
        """
        tax_amount = subtotal * (tax_rate / 100) if tax_rate > 0 else 0
        total = subtotal - discount + tax_amount
        
        total_data = [
            ['', '', '', 'Subtotal:', f"${subtotal:.2f}"],
            ['', '', '', 'Discount:', f"-${discount:.2f}"],
            ['', '', '', 'Tax:', f"${tax_amount:.2f}"],
            ['', '', '', '<b>Total:</b>', f"<b>${total:.2f}</b>"],
        ]
        
        total_table = Table(
            total_data,
            colWidths=[1.5*cm, 8*cm, 2*cm, 2.5*cm, 2*cm]
        )
        
        total_table.setStyle(TableStyle([
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (3, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (3, 0), (-1, -1), 11),
            ('FONTNAME', (3, 3), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (3, 3), (-1, -1), 12),
            ('TEXTCOLOR', (3, 3), (-1, -1), colors.HexColor('#d32f2f')),
            ('LINEABOVE', (3, 0), (-1, 0), 1, colors.grey),
            ('LINEBELOW', (3, 3), (-1, 3), 2, colors.HexColor('#d32f2f')),
        ]))
        
        self.story.append(total_table)
        self.story.append(Spacer(1, 1*cm))
    
    def add_footer(self, notes: Optional[str] = None, payment_info: Optional[Dict[str, str]] = None, stamp_path: Optional[str] = None):
        """
        添加发票底部信息
        
        Args:
            notes: 备注信息
            payment_info: 支付信息字典 {'bank': '', 'account': '', 'swift': ''}
            stamp_path: 图章图片路径（可选）
        """
        if notes:
            notes_style = ParagraphStyle(
                'Notes',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#666666'),
                spaceAfter=10
            )
            notes_para = Paragraph(f"<b>Notes:</b> {notes}", notes_style)
            self.story.append(notes_para)
            self.story.append(Spacer(1, 0.5*cm))
        
        if payment_info:
            payment_data = [
                ['<b>Payment Information</b>'],
                [f"Bank: {payment_info.get('bank', '')}"],
                [f"Account: {payment_info.get('account', '')}"],
                [f"SWIFT: {payment_info.get('swift', '')}"],
            ]
            
            payment_table = Table(payment_data, colWidths=[16*cm])
            payment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            self.story.append(payment_table)
            self.story.append(Spacer(1, 0.5*cm))
        
        # 添加签名区域和图章
        if stamp_path and os.path.exists(stamp_path):
            try:
                # 使用绝对路径确保能找到文件
                abs_stamp_path = os.path.abspath(stamp_path)
                if not os.path.exists(abs_stamp_path):
                    raise FileNotFoundError(f"Stamp file not found: {abs_stamp_path}")
                
                # 如果有图章，在签名区域右侧显示图章
                stamp_img = Image(abs_stamp_path, width=3*cm, height=3*cm)
                signature_data = [
                    ['Issuer Signature: _______________', stamp_img],
                    ['Customer Signature: _______________', ''],
                ]
                signature_table = Table(signature_data, colWidths=[8*cm, 8*cm])
                signature_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (0, -1), 10),
                ]))
            except Exception as e:
                print(f"Warning: Could not load stamp image: {e}")
                print(f"Stamp path: {stamp_path}")
                # 如果图章加载失败，使用默认签名区域
                signature_data = [
                    ['', ''],
                    ['Issuer Signature: _______________', 'Customer Signature: _______________'],
                ]
                signature_table = Table(signature_data, colWidths=[8*cm, 8*cm])
                signature_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
        else:
            # 没有图章时使用默认签名区域
            signature_data = [
                ['', ''],
                ['Issuer Signature: _______________', 'Customer Signature: _______________'],
            ]
            signature_table = Table(signature_data, colWidths=[8*cm, 8*cm])
            signature_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(signature_table)
    
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
    stamp_path: Optional[str] = None
) -> str:
    """
    创建发票的便捷函数
    
    Args:
        output_path: 输出PDF文件路径
        company_info: 公司信息
        customer_info: 客户信息
        invoice_info: 发票信息
        items: 项目列表
        tax_rate: 税率（百分比）
        discount: 折扣金额
        notes: 备注
        payment_info: 支付信息
        logo_path: 公司Logo图片路径（可选）
        stamp_path: 图章图片路径（可选）
    
    Returns:
        生成的PDF文件路径
    """
    generator = InvoiceGenerator(output_path)
    generator.add_header(company_info, invoice_info, logo_path)
    generator.add_customer_info(customer_info)
    generator.add_items(items)
    
    # 计算小计
    subtotal = sum(item.get('amount', item.get('quantity', 0) * item.get('unit_price', 0)) 
                   for item in items)
    
    generator.add_total(subtotal, tax_rate, discount)
    generator.add_footer(notes, payment_info, stamp_path)
    generator.generate()
    
    return output_path


