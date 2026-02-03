from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models import Customer, Order, OrderItem, Product, Transaction
from app import db
from app.decorators import role_required
from datetime import datetime

sales_bp = Blueprint('sales', __name__)

# --- Customer Routes ---
@sales_bp.route('/customers')
@login_required
@role_required('super_admin', 'admin', 'manager', 'store_user')
def customers():
    customers = Customer.query.all()
    return render_template('sales/customers.html', customers=customers, title='Customer Management')

@sales_bp.route('/customers/add', methods=['GET', 'POST'])
@login_required
@role_required('super_admin', 'admin', 'manager')
def add_customer():
    if request.method == 'POST':
        customer = Customer(
            name=request.form.get('name'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            address=request.form.get('address'),
            gstin=request.form.get('gstin')
        )
        try:
            db.session.add(customer)
            db.session.commit()
            flash('Customer added successfully!', 'success')
            return redirect(url_for('sales.customers'))
        except Exception as e:
            flash(f'Error adding customer: {str(e)}', 'danger')
    return render_template('sales/customer_form.html', title='Add Customer')

@sales_bp.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('super_admin', 'admin', 'manager')
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        customer.name = request.form.get('name')
        customer.phone = request.form.get('phone')
        customer.email = request.form.get('email')
        customer.address = request.form.get('address')
        customer.gstin = request.form.get('gstin')
        try:
            db.session.commit()
            flash('Customer updated successfully!', 'success')
            return redirect(url_for('sales.customers'))
        except Exception as e:
            flash(f'Error updating customer: {str(e)}', 'danger')
    return render_template('sales/customer_form.html', customer=customer, title='Edit Customer')

# --- Sales Order Routes ---
@sales_bp.route('/sales/orders')
@login_required
def orders():
    orders = Order.query.filter_by(type='SALE').order_by(Order.date.desc()).all()
    return render_template('sales/orders.html', orders=orders, title='Sales Orders')

@sales_bp.route('/sales/new', methods=['GET', 'POST'])
@login_required
def create_order():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        discount = float(request.form.get('discount') or 0)
        
        # Create Order Header
        order = Order(
            type='SALE',
            customer_id=customer_id,
            status='COMPLETED', 
            date=datetime.utcnow(),
            discount=discount
        )
        db.session.add(order)
        db.session.flush() 
        
        total_amount = 0
        error_msg = None
        
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        
        # Process items
        for pid, qty in zip(product_ids, quantities):
            if pid and qty:
                qty = int(qty)
                product = Product.query.get(pid)
                
                if product.stock_quantity < qty:
                    error_msg = f'Insufficient stock for {product.name}. Available: {product.stock_quantity}'
                    break
                
                price = product.selling_price
                line_total = qty * float(price)
                
                item = OrderItem(
                    order_id=order.id,
                    product_id=pid,
                    quantity=qty,
                    price=price,
                    total=line_total
                )
                db.session.add(item)
                total_amount += line_total
                
                # Update Stock
                product.stock_quantity -= qty
                
                # Log Transaction
                txn = Transaction(
                    product_id=pid,
                    type='OUT',
                    quantity=qty,
                    reference_model='Order',
                    reference_id=order.id,
                    description=f'Sale to Customer {customer_id}'
                )
                db.session.add(txn)

        if error_msg:
            db.session.rollback()
            flash(error_msg, 'danger')
            return redirect(url_for('sales.create_order'))

        order.total_amount = total_amount
        order.grand_total = total_amount - discount
        
        try:
            db.session.commit()
            
            # Send Email Notification
            try:
                from app.email_service import EmailService
                EmailService.send_sales_order_confirmation(order, Customer.query.get(customer_id) if customer_id else None)
            except Exception as email_error:
                print(f"Email notification failed: {email_error}")
            
            flash('Sales Order created and Stock Updated! Email sent.', 'success')
            return redirect(url_for('sales.invoice', id=order.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating order: {str(e)}', 'danger')

    customers = Customer.query.all()
    products = Product.query.filter(Product.stock_quantity > 0).all() # Only show products with stock
    return render_template('sales/create_order.html', customers=customers, products=products, title='New Sales Order')

@sales_bp.route('/sales/invoice/<int:id>')
@login_required
def invoice(id):
    order = Order.query.get_or_404(id)
    if order.type != 'SALE':
        abort(404)
    return render_template('sales/invoice.html', order=order)
