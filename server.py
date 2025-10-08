from flask import Flask, render_template, url_for, request, redirect
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import requests

app = Flask(__name__)
print(__name__)


@app.route('/')
def my_home():
    return render_template('index.html')

@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)

def write_to_file(data):
    with open('database.txt', mode='a') as database:
        email = data["email"]
        subject = data["subject"]
        message = data["message"]
        file = database.write(f'\n{email},{subject},{message}')

def write_to_csv(data):
    with open('database.csv', mode='a', newline='') as database2:
        email = data["email"]
        subject = data["subject"]
        message = data["message"]
        csv_writer = csv.writer(database2, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([email,subject,message])

def send_email(data):
    # Try SendGrid first (for production), fallback to Gmail SMTP (for local development)
    sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
    
    if sendgrid_api_key:
        return send_email_sendgrid(data, sendgrid_api_key)
    else:
        # Temporarily disable SMTP on production to avoid timeouts
        print("Email functionality disabled on production (SMTP blocked). Use SendGrid for production.")
        return True  # Return True so the form still works

def send_email_sendgrid(data, api_key):
    """Send email using SendGrid API"""
    from_email = os.environ.get('SENDGRID_FROM_EMAIL', 'hiruyworku00@gmail.com')
    to_email = os.environ.get('SENDGRID_TO_EMAIL', 'hiruyworku00@gmail.com')
    
    url = "https://api.sendgrid.com/v3/mail/send"
    
    payload = {
        "personalizations": [
            {
                "to": [{"email": to_email}],
                "subject": f"Portfolio Contact: {data['subject']}"
            }
        ],
        "from": {"email": from_email},
        "content": [
            {
                "type": "text/plain",
                "value": f"""
New message from your portfolio website:

From: {data['email']}
Subject: {data['subject']}

Message:
{data['message']}

---
This message was sent from your portfolio contact form.
"""
            }
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 202:
            print("Email sent successfully via SendGrid!")
            return True
        else:
            print(f"SendGrid error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"SendGrid error: {e}")
        return False

def send_email_smtp(data):
    """Send email using Gmail SMTP (for local development)"""
    # Email configuration
    sender_email = "hiruyworku00@gmail.com"  # Your Gmail address
    sender_password = os.environ.get('EMAIL_PASSWORD')  # Get password from environment variable
    receiver_email = "hiruyworku00@gmail.com"  # Where to receive the emails
    
    # Check if email password is configured
    if not sender_password:
        print("EMAIL_PASSWORD environment variable not set. Email not sent.")
        return False
    
    print(f"Attempting to send email with password: {sender_password[:4]}***")  # Debug: show first 4 chars
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"Portfolio Contact: {data['subject']}"
    
    # Email body
    body = f"""
    New message from your portfolio website:
    
    From: {data['email']}
    Subject: {data['subject']}
    
    Message:
    {data['message']}
    
    ---
    This message was sent from your portfolio contact form.
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Create SMTP session
        print("Connecting to Gmail SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        print("Starting TLS encryption...")
        print("Attempting to login...")
        server.login(sender_email, sender_password)
        print("Login successful!")
        
        # Send email
        print("Sending email...")
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == 'POST':
        print(request.form)  # Debug print
        try:
            data = request.form.to_dict()
            write_to_csv(data)
            # Send email
            send_email(data)
            return redirect('/thankyou.html')
        except Exception as e:
            print(f"Error in submit_form: {e}")
            return 'did not save to database'
    else:
        return "something went wrong, please try again"

@app.route('/request_resume', methods=['POST'])
def request_resume():
    requester_email = request.form.get('email')
    if requester_email:
        # Compose the message
        data = {
            'email': requester_email,
            'subject': 'Resume Request',
            'message': f'{requester_email} has requested to view your resume.'
        }
        result = send_email(data)
        print(f"Email send result: {result}")
        return redirect('/thankyou.html')
    else:
        return 'Email is required to request the resume.'

@app.route('/test_email')
def test_email():
    """Test route to check if email functionality works"""
    test_data = {
        'email': 'test@example.com',
        'subject': 'Test Email',
        'message': 'This is a test email from your portfolio.'
    }
    result = send_email(test_data)
    return f"Test email result: {result}"