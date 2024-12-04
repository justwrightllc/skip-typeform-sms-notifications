# requirements.txt
flask==2.0.1
twilio==7.17.0
python-dotenv==0.19.0
pytz==2021.1
gunicorn==20.1.0

# .env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_number
YOUR_PHONE_NUMBER=your_personal_number

# Procfile
web: gunicorn app:app

# app.py
from flask import Flask, request
from twilio.rest import Client
import os
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
YOUR_PHONE_NUMBER = os.getenv('YOUR_PHONE_NUMBER')

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route('/')
def home():
    return 'Typeform SMS Notification Service is running!'

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Get the form response data
        data = request.json
        form_response = data['form_response']
        
        # Extract answers
        answers = form_response['answers']
        
        # Create a message with the lead's information
        message = "New Charter Lead!\n\n"
        
        # Process each answer
        for answer in answers:
            if answer['type'] == 'text' or answer['type'] == 'email':
                field_value = answer['text']
            elif answer['type'] == 'phone_number':
                field_value = answer['phone_number']
            elif answer['type'] == 'date':
                field_value = answer['date']
            else:
                continue
                
            # Add the field to the message
            message += f"{answer['field']['title']}: {field_value}\n"
        
        # Add timestamp
        eastern = pytz.timezone('US/Eastern')
        timestamp = datetime.now(eastern).strftime('%Y-%m-%d %I:%M %p %Z')
        message += f"\nReceived: {timestamp}"
        
        # Send SMS
        twilio_client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=YOUR_PHONE_NUMBER
        )
        
        return 'OK', 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 'Error', 500

if __name__ == '__main__':
    app.run(port=5000)
