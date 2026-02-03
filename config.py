import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string-for-dev'
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

    # Fallback to SQLite for development ease if MySQL/Postgres is not configured
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'erp.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email Configuration
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY') or 're_jJauwrBT_MdiVhGE9ZruYJyD1WXUZSSE1'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'vp2524267@gmail.com'
    EMAIL_FROM = 'ERP System <onboarding@resend.dev>'  # Resend default sender
    
    # Email Notifications Settings
    ENABLE_EMAIL_NOTIFICATIONS = True
    LOW_STOCK_EMAIL_ENABLED = True
    ORDER_EMAIL_ENABLED = True
    DAILY_REPORT_EMAIL_ENABLED = True
    
    # Pagination
    ITEMS_PER_PAGE = 20

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    # Ensure strong secret key in production
    SECRET_KEY = os.environ.get('SECRET_KEY')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
