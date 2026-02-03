from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import Product, Transaction
from app import db
from app.decorators import role_required

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory')
@login_required
@role_required('super_admin', 'admin', 'manager', 'store_user')
def index():
    products = Product.query.all()
    return render_template('inventory/index.html', products=products, title='Inventory Management')

@inventory_bp.route('/inventory/add', methods=['GET', 'POST'])
@login_required
@role_required('super_admin', 'admin', 'manager')
def add_product():
    if request.method == 'POST':
        code = request.form.get('code')
        if Product.query.filter_by(code=code).first():
            flash(f'Error: Product code {code} already exists!', 'danger')
            return render_template('inventory/form.html', title='Add Product')

        product = Product(
            code=code,
            name=request.form.get('name'),
            category=request.form.get('category'),
            brand=request.form.get('brand'),
            unit=request.form.get('unit'),
            cost_price=request.form.get('cost_price'),
            selling_price=request.form.get('selling_price'),
            gst_percent=request.form.get('gst_percent'),
            stock_quantity=request.form.get('stock_quantity'),
            min_stock_alert=request.form.get('min_stock_alert'),
            warehouse_location=request.form.get('warehouse_location')
        )
        
        try:
            db.session.add(product)
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('inventory.index'))
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed' in str(e):
                flash(f'Error: Product code {code} must be unique.', 'danger')
            else:
                flash(f'Error adding product: {str(e)}', 'danger')

    return render_template('inventory/form.html', title='Add Product')

@inventory_bp.route('/inventory/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('super_admin', 'admin', 'manager')
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.code = request.form.get('code')
        product.name = request.form.get('name')
        product.category = request.form.get('category')
        product.brand = request.form.get('brand')
        product.unit = request.form.get('unit')
        product.cost_price = request.form.get('cost_price')
        product.selling_price = request.form.get('selling_price')
        product.gst_percent = request.form.get('gst_percent')
        product.min_stock_alert = request.form.get('min_stock_alert')
        product.warehouse_location = request.form.get('warehouse_location')
        
        try:
            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('inventory.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'danger')

    return render_template('inventory/form.html', product=product, title='Edit Product')

@inventory_bp.route('/inventory/delete/<int:id>')
@login_required
@role_required('super_admin', 'admin')
def delete_product(id):
    product = Product.query.get_or_404(id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        flash('Cannot delete product. It might be linked to existing orders.', 'danger')
    return redirect(url_for('inventory.index'))
