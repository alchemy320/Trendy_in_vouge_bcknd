from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import get_access_token, generate_password
import requests
from django.conf import settings

class InitiatePaymentView(APIView):
    def post(self, request):
        # Extract data from request
        phone_number = request.data.get('phone_number')
        amount = request.data.get('amount')
        account_reference = request.data.get('account_reference', 'TestRef')
        transaction_desc = request.data.get('transaction_desc', 'Payment for goods')

        if not phone_number or not amount:
            return Response({'error': 'Missing phone_number or amount'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            access_token = get_access_token()
            password, timestamp = generate_password()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "BusinessShortCode": settings.DARAJA_SHORT_CODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": settings.DARAJA_SHORT_CODE,
            "PhoneNumber": phone_number,
            "CallBackURL": settings.DARAJA_CALLBACK_URL,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }

        response = requests.post(
            'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            return Response(response.json())
        else:
            return Response(response.json(), status=response.status_code)

class MpesaCallbackView(APIView):
    def post(self, request):
        data = request.data
        # Here, you can process the callback data, save to DB, etc.
        return Response({'status': 'Callback received', 'data': data})