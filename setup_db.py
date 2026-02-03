from app import create_app, db
from app.models import User

app = create_app('development')

def setup_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created.")

        # Check if admin exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@erp.com',
                role='super_admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Add a manager user
            manager = User(
                username='manager',
                email='manager@erp.com',
                role='manager',
                is_active=True
            )
            manager.set_password('manager123')
            db.session.add(manager)
            
            db.session.commit()
            print("Super Admin and Manager users created.")
            print("Admin Creds: admin / admin123")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    setup_database()
