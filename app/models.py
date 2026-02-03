from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

# --- Settings Model ---
class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)

# --- Authentication Models ---
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    # Role: 'super_admin', 'admin', 'manager', 'store_user'
    role = db.Column(db.String(20), nullable=False, default='store_user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, *roles):
        return self.role in roles

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


# --- Inventory Models ---
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False) # Auto-generated or manual
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    brand = db.Column(db.String(50))
    unit = db.Column(db.String(20)) # Kg, Packet, Box
    cost_price = db.Column(db.Numeric(10, 2))
    selling_price = db.Column(db.Numeric(10, 2))
    gst_percent = db.Column(db.Numeric(5, 2), default=0.0)
    stock_quantity = db.Column(db.Integer, default=0)
    min_stock_alert = db.Column(db.Integer, default=10)
    batch_number = db.Column(db.String(50))
    expiry_date = db.Column(db.Date)
    warehouse_location = db.Column(db.String(100))
    
    # Relationships
    transactions = db.relationship('Transaction', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

class Transaction(db.Model):
    """Tracks stock history"""
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False) # 'IN', 'OUT'
    quantity = db.Column(db.Integer, nullable=False)
    reference_model = db.Column(db.String(50)) # 'Order', 'Adjustment'
    reference_id = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(200))


# --- Purchase Models ---
class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    gstin = db.Column(db.String(20))
    
    orders = db.relationship('Order', backref='supplier', lazy=True, foreign_keys='Order.supplier_id')

# --- Sales Models ---
class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    gstin = db.Column(db.String(20))
    
    orders = db.relationship('Order', backref='customer', lazy=True, foreign_keys='Order.customer_id')

# --- Common Order Models (Purchase & Sales) ---
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False) # 'PURCHASE' or 'SALE'
    
    # Nullable Foreign Keys because an order is either from supplier OR customer
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='PENDING') # 'PENDING', 'COMPLETED', 'CANCELLED'
    total_amount = db.Column(db.Numeric(12, 2), default=0.0)
    discount = db.Column(db.Numeric(12, 2), default=0.0)
    tax_amount = db.Column(db.Numeric(12, 2), default=0.0)
    grand_total = db.Column(db.Numeric(12, 2), default=0.0)
    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False) # Cost Price for Purchase, Selling Price for Sales
    tax_amount = db.Column(db.Numeric(10, 2), default=0.0)
    total = db.Column(db.Numeric(10, 2), nullable=False)
