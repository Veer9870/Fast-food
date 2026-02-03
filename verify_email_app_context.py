
import os
from app import create_app
from app.email_service import EmailService

app = create_app('default')

with app.app_context():
    print("Testing EmailService within App Context...")
    print(f"API Key from config: {app.config.get('RESEND_API_KEY')[:5]}...")
    print(f"Enable Email: {app.config.get('ENABLE_EMAIL_NOTIFICATIONS')}")
    
    to_email = "vp2524267@gmail.com"
    subject = "Test Email from App Context"
    html = "<p>This is a test email sent from the ERP application context.</p>"
    
    print("Attempting to send email...")
    success = EmailService._send_email(to_email, subject, html)
    
    if success:
        print("SUCCESS: Email sent successfully via EmailService.")
    else:
        print("FAILURE: EmailService returned False.")
