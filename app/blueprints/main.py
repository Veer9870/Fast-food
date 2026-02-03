from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

from app.models import Setting
from app import db # Need db for saving settings

@main_bp.context_processor
def inject_company_info():
    # Helper to available globally
    def get_setting(key, default=''):
        s = Setting.query.filter_by(key=key).first()
        return s.value if s else default
    return dict(get_setting=get_setting)

@main_bp.route('/')
@login_required
def dashboard():
    from app.models import Product, Order, OrderItem
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # Total Products
    total_products = Product.query.count()
    
    # Total Stock Value (Cost Price × Quantity)
    stock_value = db.session.query(
        func.sum(Product.cost_price * Product.stock_quantity)
    ).scalar() or 0
    
    # Low Stock Alerts
    low_stock_count = Product.query.filter(
        Product.stock_quantity <= Product.min_stock_alert
    ).count()
    
    # Today's Sales
    today = datetime.now().date()
    today_sales = db.session.query(
        func.sum(Order.grand_total)
    ).filter(
        Order.type == 'SALE',
        func.date(Order.date) == today
    ).scalar() or 0
    
    # Last 7 Days Sales (for chart)
    sales_data = []
    sales_labels = []
    for i in range(6, -1, -1):
        day = datetime.now() - timedelta(days=i)
        day_total = db.session.query(
            func.sum(Order.grand_total)
        ).filter(
            Order.type == 'SALE',
            func.date(Order.date) == day.date()
        ).scalar() or 0
        sales_data.append(float(day_total))
        sales_labels.append(day.strftime('%d %b'))
    
    # Top 5 Selling Products (by quantity sold)
    top_products = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label('total_qty')
    ).join(OrderItem).join(Order).filter(
        Order.type == 'SALE'
    ).group_by(Product.id).order_by(func.sum(OrderItem.quantity).desc()).limit(5).all()
    
    top_product_names = [p[0] for p in top_products]
    top_product_quantities = [int(p[1]) for p in top_products]
    
    # Category-wise Stock Distribution
    category_stock = db.session.query(
        Product.category,
        func.sum(Product.stock_quantity).label('total_stock')
    ).group_by(Product.category).all()
    
    category_names = [c[0] or 'Uncategorized' for c in category_stock]
    category_quantities = [int(c[1]) for c in category_stock]
    
    # Low Stock Products
    low_stock_products = Product.query.filter(
        Product.stock_quantity <= Product.min_stock_alert
    ).limit(5).all()
    
    # Send Email if low stock detected and not sent today
    if low_stock_count > 0:
        try:
            from app.email_service import EmailService
            all_low_stock = Product.query.filter(
                Product.stock_quantity <= Product.min_stock_alert
            ).all()
            # Only send email once per day per product - you could add more complex logic here
            EmailService.send_low_stock_alert(all_low_stock)
        except Exception as e:
            print(f"Low stock email failed: {e}")
    
    return render_template('dashboard/index.html', 
                         title='Dashboard',
                         total_products=total_products,
                         stock_value=round(stock_value, 2),
                         low_stock_count=low_stock_count,
                         today_sales=round(today_sales, 2),
                         sales_labels=sales_labels,
                         sales_data=sales_data,
                         top_product_names=top_product_names,
                         top_product_quantities=top_product_quantities,
                         category_names=category_names,
                         category_quantities=category_quantities,
                         low_stock_products=low_stock_products)

@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        keys = ['company_name', 'company_address', 'company_phone', 'default_gst_percent', 'financial_year']
        
        try:
            for key in keys:
                val = request.form.get(key)
                setting = Setting.query.filter_by(key=key).first()
                if not setting:
                    setting = Setting(key=key, value=val)
                    db.session.add(setting)
                else:
                    setting.value = val
            db.session.commit()
            flash('Settings saved successfully!', 'success')
        except Exception as e:
            flash(f'Error saving settings: {str(e)}', 'danger')
            
    return render_template('settings.html', title='System Settings')

