import requests
from django.conf import settings
import base64
from datetime import datetime

def get_access_token():
    """
    Fetches the OAuth access token from Daraja API.
    """
    url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    credentials = f"{settings.DARAJA_CONSUMER_KEY}:{settings.DARAJA_CONSUMER_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {
        'Authorization': f'Basic {encoded_credentials}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Failed to get access token: {response.text}")

def generate_password():
    """
    Generates the password for STK Push request.
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = settings.DARAJA_SHORT_CODE + settings.DARAJA_PASSKEY + timestamp
    encoded_string = base64.b64encode(data_to_encode.encode()).decode()
    return encoded_string, timestamp