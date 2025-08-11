import logging
import requests
import certifi
from django.conf import settings
from django_daraja.mpesa.core import MpesaClient
from datetime import datetime
import base64

logger = logging.getLogger(__name__)

class DebugMpesaClient(MpesaClient):
    """Custom MpesaClient that logs token request/response using updated certifi CA bundle."""

    def get_access_token(self):
        token_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        logger.info(f"Requesting access token from: {token_url}")
        logger.info(f"Using key: {settings.MPESA_CONSUMER_KEY}")
        logger.info(f"Using secret: {settings.MPESA_CONSUMER_SECRET}")

        r = requests.get(
            token_url,
            auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
            verify=certifi.where()
        )
        logger.info(f"Access token response [{r.status_code}]: {r.text}")

        if r.status_code != 200:
            raise Exception(f"Failed to get access token: {r.text}")

        return r.json().get("access_token")

    def stk_push(self, phone_number, amount, account_reference, transaction_desc, callback_url):
        # Get the token manually with proper SSL verification
        access_token = self.get_access_token()
        logger.info(f"Using access token: {access_token}")

        # Continue with parent class STK push
        return super().stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)


def generate_password(shortcode, passkey):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = shortcode + passkey.strip() + timestamp
    encoded_string = base64.b64encode(data_to_encode.encode())
    return encoded_string.decode('utf-8'), timestamp


def stk_push_direct(phone_number, amount, account_reference, transaction_desc, callback_url):
    # Get access token
    cl = DebugMpesaClient()
    access_token = cl.get_access_token()

    # Generate password & timestamp
    password, timestamp = generate_password(settings.MPESA_SHORTCODE.strip(), settings.MPESA_PASSKEY)

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE.strip(),
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE.strip(),
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    logger.info(f"Sending STK Push request: {payload}")

    r = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers=headers,
        verify=certifi.where()
    )

    logger.info(f"STK Push response [{r.status_code}]: {r.text}")
    return r.json()
