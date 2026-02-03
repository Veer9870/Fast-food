from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Supplier, Order, OrderItem, Product, Transaction
from app import db
from app.decorators import role_required
from datetime import datetime

purchase_bp = Blueprint('purchase', __name__)

# --- Supplier Routes ---
@purchase_bp.route('/suppliers')
@login_required
@role_required('super_admin', 'admin', 'manager')
def suppliers():
    suppliers = Supplier.query.all()
    return render_template('purchase/suppliers.html', suppliers=suppliers, title='Supplier Management')

@purchase_bp.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
@role_required('super_admin', 'admin', 'manager')
def add_supplier():
    if request.method == 'POST':
        supplier = Supplier(
            name=request.form.get('name'),
            contact_person=request.form.get('contact_person'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            address=request.form.get('address'),
            gstin=request.form.get('gstin')
        )
        try:
            db.session.add(supplier)
            db.session.commit()
            flash('Supplier added successfully!', 'success')
            return redirect(url_for('purchase.suppliers'))
        except Exception as e:
            flash(f'Error adding supplier: {str(e)}', 'danger')
    return render_template('purchase/supplier_form.html', title='Add Supplier')

@purchase_bp.route('/suppliers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('super_admin', 'admin', 'manager')
def edit_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    if request.method == 'POST':
        supplier.name = request.form.get('name')
        supplier.contact_person = request.form.get('contact_person')
        supplier.phone = request.form.get('phone')
        supplier.email = request.form.get('email')
        supplier.address = request.form.get('address')
        supplier.gstin = request.form.get('gstin')
        try:
            db.session.commit()
            flash('Supplier updated successfully!', 'success')
            return redirect(url_for('purchase.suppliers'))
        except Exception as e:
            flash(f'Error updating supplier: {str(e)}', 'danger')
    return render_template('purchase/supplier_form.html', supplier=supplier, title='Edit Supplier')

# --- Purchase Order Routes ---
@purchase_bp.route('/purchase/orders')
@login_required
@role_required('super_admin', 'admin', 'manager')
def orders():
    orders = Order.query.filter_by(type='PURCHASE').order_by(Order.date.desc()).all()
    return render_template('purchase/orders.html', orders=orders, title='Purchase Orders')

@purchase_bp.route('/purchase/new', methods=['GET', 'POST'])
@login_required
@role_required('super_admin', 'admin', 'manager')
def create_order():
    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id')
        
        # Create Order Header
        order = Order(
            type='PURCHASE',
            supplier_id=supplier_id,
            status='COMPLETED', # For simplicity, auto-complete. In real apps, usually PENDING -> GRN -> COMPLETED
            date=datetime.utcnow()
        )
        db.session.add(order)
        db.session.flush() # Get ID
        
        total_amount = 0
        
        # Handle Items (Assuming dynamic form with array inputs)
        # In a real app, this would be JS-heavy. Here we assume one item for simplicity or use a loop if inputs are named properly.
        # Let's support multiple items via list parsing
        
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')
        
        for pid, qty, price in zip(product_ids, quantities, prices):
            if pid and qty and price:
                qty = int(qty)
                price = float(price)
                line_total = qty * price
                
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
                product = Product.query.get(pid)
                product.stock_quantity += qty
                # Update cost price to latest purchase price? Optional. 
                # product.cost_price = price 
                
                # Log Transaction
                txn = Transaction(
                    product_id=pid,
                    type='IN',
                    quantity=qty,
                    reference_model='Order',
                    reference_id=order.id,
                    description=f'Purchase from Supplier {supplier_id}'
                )
                db.session.add(txn)

        order.total_amount = total_amount
        order.grand_total = total_amount # Tax logic can be added here
        
        try:
            db.session.commit()
            
            # Send Email Notification
            try:
                from app.email_service import EmailService
                EmailService.send_purchase_order_confirmation(order, Supplier.query.get(supplier_id))
            except Exception as email_error:
                import traceback
                print(f"Email notification failed: {email_error}")
                traceback.print_exc()
            
            flash('Purchase Order created and Stock Updated! Email sent.', 'success')
            return redirect(url_for('purchase.orders'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating order: {str(e)}', 'danger')

    suppliers = Supplier.query.all()
    products = Product.query.all()
    return render_template('purchase/create_order.html', suppliers=suppliers, products=products, title='New Purchase Order')
