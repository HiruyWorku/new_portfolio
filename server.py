from flask import Flask, render_template, request, redirect
import os
import requests

app = Flask(__name__)


@app.route('/')
def my_home():
    return render_template('index.html')

@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)


def send_email(data):
    api_key = os.environ.get('RESEND_API_KEY')
    to_email = os.environ.get('RESEND_TO_EMAIL', 'hiruyworku00@gmail.com')

    if not api_key:
        print("RESEND_API_KEY not set — email not sent.")
        return False, "no api key"

    payload = {
        "from": "Portfolio Contact <onboarding@resend.dev>",
        "to": [to_email],
        "subject": f"Portfolio Contact: {data['subject']}",
        "text": (
            f"New message from your portfolio:\n\n"
            f"From: {data['email']}\n"
            f"Subject: {data['subject']}\n\n"
            f"{data['message']}"
        )
    }

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )
        print(f"Resend status: {response.status_code} — {response.text}")
        return response.status_code == 200, response.text
    except Exception as e:
        print(f"Resend error: {e}")
        return False, str(e)




@app.route('/submit_form', methods=['POST'])
def submit_form():
    data = request.form.to_dict()
    ok, detail = send_email(data)
    print(f"submit_form email result: {ok} — {detail}")
    return redirect('/thankyou.html')


@app.route('/request_resume', methods=['POST'])
def request_resume():
    requester_email = request.form.get('email')
    if not requester_email:
        return 'Email is required.', 400
    send_email({
        'email': requester_email,
        'subject': 'Resume Request',
        'message': f'{requester_email} has requested to view your resume.'
    })
    return redirect('/thankyou.html')
