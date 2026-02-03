import os
import resend

# Configuration
API_KEY = "re_jJauwrBT_MdiVhGE9ZruYJyD1WXUZSSE1"  # Hardcoded from config.py for testing
FROM_EMAIL = "onboarding@resend.dev"
TO_EMAIL = "vp2524267@gmail.com"  # The only verified email likely

print(f"Testing Resend API...")
print(f"API Key: {API_KEY[:5]}...")
print(f"From: {FROM_EMAIL}")
print(f"To: {TO_EMAIL}")

resend.api_key = API_KEY

try:
    params = {
        "from": FROM_EMAIL,
        "to": [TO_EMAIL],
        "subject": "Resend API Test Script",
        "html": "<p>This is a direct test of the Resend API from a python script.</p>"
    }
    
    print("Sending...")
    email = resend.Emails.send(params)
    print(f"Response: {email}")
    print("SUCCESS: Check your inbox!")

except Exception as e:
    print(f"ERROR: {e}")
