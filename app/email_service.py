"""
Email Service for ERP System using Resend API
Handles all email notifications including:
- Low stock alerts
- Order confirmations (Purchase & Sales)
- Daily/Weekly reports
"""

import resend
from flask import current_app, render_template_string
from datetime import datetime
import resend
from io import BytesIO
from xhtml2pdf import pisa

class EmailService:
    """Email notification service using Resend API"""

    @staticmethod
    def generate_pdf(html_content):
        """Generate PDF from HTML content"""
        output = BytesIO()
        pisa_status = pisa.CreatePDF(
            html_content, dest=output
        )
        if pisa_status.err:
            print(f"[ERROR] PDF generation failed: {pisa_status.err}")
            return None
        return output.getvalue()
    
    @staticmethod
    def _send_email(to_email, subject, html_content, attachments=None):
        """Internal method to send email via Resend"""
        try:
            if not current_app.config.get('ENABLE_EMAIL_NOTIFICATIONS'):
                print(f"Email notifications disabled. Would send: {subject} to {to_email}")
                return False
            
            resend.api_key = current_app.config['RESEND_API_KEY']
            
            if isinstance(to_email, list):
                recipients = to_email
            else:
                recipients = [to_email]

            params = {
                "from": current_app.config['EMAIL_FROM'],
                "to": recipients,
                "subject": subject,
                "html": html_content,
                "attachments": attachments or []
            }
            
            email = resend.Emails.send(params)
            print(f"[SUCCESS] Email sent successfully: {subject}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Email sending failed: {str(e)}")
            return False
    
    @staticmethod
    def send_low_stock_alert(products):
        """Send low stock alert email"""
        if not current_app.config.get('LOW_STOCK_EMAIL_ENABLED'):
            return
        
        html = f"""
        <h2>⚠️ Low Stock Alert - ERP System</h2>
        <p>The following products are running low on stock:</p>
        <table border="1" cellpadding="10" style="border-collapse: collapse;">
            <thead style="background-color: #f8d7da;">
                <tr>
                    <th>Product Code</th>
                    <th>Product Name</th>
                    <th>Current Stock</th>
                    <th>Minimum Required</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for product in products:
            html += f"""
                <tr>
                    <td>{product.code}</td>
                    <td>{product.name}</td>
                    <td style="color: red; font-weight: bold;">{product.stock_quantity}</td>
                    <td>{product.min_stock_alert}</td>
                </tr>
            """
        
        html += """
            </tbody>
        </table>
        <p><strong>Action Required:</strong> Please reorder these items to maintain inventory levels.</p>
        <p style="color: #666; font-size: 12px;">Generated on: """ + datetime.now().strftime('%Y-%m-%d %I:%M %p') + """</p>
        """
        
        EmailService._send_email(
            current_app.config['ADMIN_EMAIL'],
            f"🚨 Low Stock Alert - {len(products)} Products",
            html
        )
    
    @staticmethod
    def send_purchase_order_confirmation(order, supplier):
        """Send purchase order confirmation email"""
        if not current_app.config.get('ORDER_EMAIL_ENABLED'):
            return
        
        items_html = ""
        for item in order.items:
            items_html += f"""
                <tr>
                    <td>{item.product.code}</td>
                    <td>{item.product.name}</td>
                    <td>{item.quantity}</td>
                    <td>₹{item.price:.2f}</td>
                    <td>₹{item.total:.2f}</td>
                </tr>
            """
        
        html = f"""
        <h2>✅ Purchase Order Confirmation</h2>
        <p><strong>Order ID:</strong> PO-{order.id}</p>
        <p><strong>Supplier:</strong> {supplier.name}</p>
        <p><strong>Date:</strong> {order.date.strftime('%Y-%m-%d %I:%M %p')}</p>
        <p><strong>Status:</strong> <span style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 4px;">{order.status}</span></p>
        
        <h3>Order Items</h3>
        <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
            <thead style="background-color: #007bff; color: white;">
                <tr>
                    <th>Code</th>
                    <th>Product</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
            </tbody>
            <tfoot>
                <tr style="background-color: #f0f0f0; font-weight: bold;">
                    <td colspan="4" align="right">Grand Total:</td>
                    <td>₹{order.grand_total:.2f}</td>
                </tr>
            </tfoot>
        </table>
        
        <p style="margin-top: 20px;"><strong>✅ Stock has been automatically updated.</strong></p>
        <p style="color: #666; font-size: 12px;">This is an automated notification from ERP System.</p>
        """
        
        EmailService._send_email(
            current_app.config['ADMIN_EMAIL'],
            f"Purchase Order Confirmed - PO-{order.id}",
            html
        )
    
    @staticmethod
    def send_sales_order_confirmation(order, customer):
        """Send sales order confirmation email"""
        if not current_app.config.get('ORDER_EMAIL_ENABLED'):
            return
        
        items_html = ""
        for item in order.items:
            items_html += f"""
                <tr>
                    <td>{item.product.code}</td>
                    <td>{item.product.name}</td>
                    <td>{item.quantity}</td>
                    <td>₹{item.price:.2f}</td>
                    <td>₹{item.total:.2f}</td>
                </tr>
            """
        
        customer_name = customer.name if customer else "Walk-in Customer"
        
        html = f"""
        <h2>💰 Sales Order Confirmation</h2>
        <p><strong>Invoice ID:</strong> INV-{order.id}</p>
        <p><strong>Customer:</strong> {customer_name}</p>
        <p><strong>Date:</strong> {order.date.strftime('%Y-%m-%d %I:%M %p')}</p>
        <p><strong>Status:</strong> <span style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 4px;">{order.status}</span></p>
        
        <h3>Invoice Items</h3>
        <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
            <thead style="background-color: #28a745; color: white;">
                <tr>
                    <th>Code</th>
                    <th>Product</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
            </tbody>
            <tfoot style="background-color: #f0f0f0;">
                <tr>
                    <td colspan="4" align="right">Subtotal:</td>
                    <td>₹{order.total_amount:.2f}</td>
                </tr>
                <tr>
                    <td colspan="4" align="right">Discount:</td>
                    <td>-₹{order.discount:.2f}</td>
                </tr>
                <tr style="font-weight: bold; font-size: 16px;">
                    <td colspan="4" align="right">Grand Total:</td>
                    <td>₹{order.grand_total:.2f}</td>
                </tr>
            </tfoot>
        </table>
        
        <p style="margin-top: 20px;"><strong>✅ Stock has been automatically deducted.</strong></p>
        <p style="color: #666; font-size: 12px;">Thank you for your business!</p>
        """
        
        
        # Generate PDF Invoice
        pdf_bytes = EmailService.generate_pdf(html)
        attachments = []
        if pdf_bytes:
            attachments = [{
                "filename": f"Invoice-{order.id}.pdf",
                "content": list(pdf_bytes)
            }]
            
        
        # Collect Recipients
        recipients = set()
        
        # 1. Admin (Me)
        if current_app.config.get('ADMIN_EMAIL'):
            recipients.add(current_app.config['ADMIN_EMAIL'])
            
        # 2. Managers
        try:
            from app.models import User
            managers = User.query.filter_by(role='manager').all()
            for manager in managers:
                if manager.email and '@' in manager.email:
                     recipients.add(manager.email)
        except Exception:
            pass # Ignore DB errors fetching managers
            
        # 3. Customer
        if customer and customer.email and '@' in customer.email:
             recipients.add(customer.email)
        
        # Convert to list
        recipient_list = list(recipients)
        
        if recipient_list:
            EmailService._send_email(
                recipient_list,
                f"💰 Invoice - INV-{order.id}",
                html,
                attachments=attachments
            )
        else:
             print("[WARN] No recipients found for invoice email")
    
    @staticmethod
    def send_daily_summary():
        """Send daily summary report email"""
        from app.models import Product, Order
        from sqlalchemy import func
        from datetime import date
        
        if not current_app.config.get('DAILY_REPORT_EMAIL_ENABLED'):
            return
        
        today = date.today()
        
        # Today's stats
        from app import db
        today_sales = db.session.query(func.sum(Order.grand_total)).filter(
            Order.type == 'SALE',
            func.date(Order.date) == today
        ).scalar() or 0
        
        today_purchases = db.session.query(func.sum(Order.total_amount)).filter(
            Order.type == 'PURCHASE',
            func.date(Order.date) == today
        ).scalar() or 0
        
        low_stock_count = Product.query.filter(
            Product.stock_quantity <= Product.min_stock_alert
        ).count()
        
        total_products = Product.query.count()
        
        html = f"""
        <h2>📊 Daily Summary Report - {today.strftime('%d %B %Y')}</h2>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3>Key Metrics</h3>
            <table style="width: 100%;">
                <tr>
                    <td style="padding: 10px;">
                        <strong>💰 Today's Sales:</strong>
                    </td>
                    <td style="padding: 10px; text-align: right; font-size: 20px; color: #28a745;">
                        ₹{today_sales:.2f}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 10px;">
                        <strong>🛒 Today's Purchases:</strong>
                    </td>
                    <td style="padding: 10px; text-align: right; font-size: 20px; color: #ffc107;">
                        ₹{today_purchases:.2f}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 10px;">
                        <strong>⚠️ Low Stock Items:</strong>
                    </td>
                    <td style="padding: 10px; text-align: right; font-size: 20px; color: #dc3545;">
                        {low_stock_count}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 10px;">
                        <strong>📦 Total Products:</strong>
                    </td>
                    <td style="padding: 10px; text-align: right; font-size: 20px; color: #007bff;">
                        {total_products}
                    </td>
                </tr>
            </table>
        </div>
        
        <p><strong>Access your ERP Dashboard:</strong> <a href="http://127.0.0.1:5000">Login to ERP</a></p>
        <p style="color: #666; font-size: 12px;">This is an automated daily report from your ERP System.</p>
        """
        
        EmailService._send_email(
            current_app.config['ADMIN_EMAIL'],
            f"📊 Daily Report - {today.strftime('%d %b %Y')}",
            html
        )
