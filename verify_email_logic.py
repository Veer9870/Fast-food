
import logging
from datetime import datetime
from app import create_app
from app.email_service import EmailService

# Mock Objects
class MockProduct:
    def __init__(self, code, name, price):
        self.code = code
        self.name = name
        self.price = price
        self.selling_price = price

class MockItem:
    def __init__(self, product, quantity, price):
        self.product = product
        self.quantity = quantity
        self.price = price
        self.total = quantity * price

class MockOrder:
    def __init__(self, id, type, items):
        self.id = id
        self.type = type
        self.items = items
        self.date = datetime.now()
        self.status = 'COMPLETED'
        self.total_amount = sum(item.total for item in items)
        self.grand_total = self.total_amount
        self.discount = 0

class MockActor:
    def __init__(self, name, email):
        self.name = name
        self.email = email

app = create_app('default')

with app.app_context():
    print("=== Testing Email Logic ===")
    
    # Setup Data
    prod1 = MockProduct('P001', 'Test Widget', 100.0)
    item1 = MockItem(prod1, 2, 100.0)
    order = MockOrder(12345, 'PURCHASE', [item1])
    supplier = MockActor('Test Supplier', 'test@example.com')
    customer = MockActor('Test Customer', 'test@example.com') # Warning: This might fail in Resend Sandbox
    
    # 1. Test Purchase Order (Simple)
    print("\n--- Testing Purchase Order Email ---")
    try:
        EmailService.send_purchase_order_confirmation(order, supplier)
        print("Called send_purchase_order_confirmation. Check console for SUCCESS/ERROR.")
    except Exception as e:
        print(f"EXCEPTION in Purchase Order: {e}")

    # 2. Test Sales Order (Complex - PDF + Multiple Recipients)
    print("\n--- Testing Sales Order Email ---")
    order.type = 'SALE'
    try:
        EmailService.send_sales_order_confirmation(order, customer)
        print("Called send_sales_order_confirmation. Check console for SUCCESS/ERROR.")
    except Exception as e:
        print(f"EXCEPTION in Sales Order: {e}")
