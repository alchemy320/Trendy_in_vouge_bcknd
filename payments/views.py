import base64
from datetime import datetime

import requests

from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Payment
from .serializer import PaymentSerializer

from orders.models import Order


# ============================================================
# TEST PAYMENT
# ============================================================

class PaymentTestView(APIView):

    def post(self, request):

        serializer = PaymentSerializer(data=request.data)

        if serializer.is_valid():

            return Response(
                {
                    "message": "Payment endpoint hit successfully.",
                    "data": serializer.validated_data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


# ============================================================
# M-PESA STK PUSH
# ============================================================

class MpesaSTKPushView(APIView):

    def post(self, request):

        print("\n========================================")
        print("M-PESA STK PUSH REQUEST")
        print("========================================")
        print("REQUEST DATA:", request.data)

        # ----------------------------------------------------
        # VALIDATE REQUEST
        # ----------------------------------------------------

        serializer = PaymentSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            print("SERIALIZER ERRORS:", serializer.errors)

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data

        order = validated_data["order"]
        amount = validated_data["amount"]
        phone_number = validated_data["phone_number"]

        account_reference = validated_data.get(
            "account_reference"
        ) or f"TRENDY-ORDER-{order.id}"

        description = validated_data.get(
            "description"
        ) or f"Trendy InVogue Order #{order.id}"

        # ----------------------------------------------------
        # MAKE SURE ORDER BELONGS TO LOGGED-IN USER
        # ----------------------------------------------------

        if order.user != request.user:

            return Response(
                {
                    "error": "You are not authorized to pay for this order."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # ----------------------------------------------------
        # MAKE SURE ORDER HAS PRODUCTS
        # ----------------------------------------------------

        if not order.orderitems.exists():

            return Response(
                {
                    "error": "This order does not contain any products."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # CREATE PAYMENT RECORD FIRST
        # ----------------------------------------------------

        payment = Payment.objects.create(
            order=order,
            phone_number=phone_number,
            amount=amount,
            account_reference=account_reference,
            description=description,
            status="PENDING"
        )

        print("PAYMENT CREATED:", payment.id)
        print("ORDER ID:", order.id)

        # ----------------------------------------------------
        # FORMAT PHONE
        # ----------------------------------------------------

        phone_number = str(phone_number).strip()

        if phone_number.startswith("0"):
            phone_number = "254" + phone_number[1:]

        elif phone_number.startswith("+254"):
            phone_number = phone_number[1:]

        elif not phone_number.startswith("254"):
            phone_number = "254" + phone_number

        print("FORMATTED PHONE:", phone_number)

        # ----------------------------------------------------
        # GET M-PESA ACCESS TOKEN
        # ----------------------------------------------------

        try:

            auth_url = (
                "https://sandbox.safaricom.co.ke/oauth/"
                "v1/generate?grant_type=client_credentials"
            )

            auth_response = requests.get(
                auth_url,
                auth=(
                    settings.MPESA_CONSUMER_KEY,
                    settings.MPESA_CONSUMER_SECRET,
                ),
                timeout=30,
            )

            auth_response.raise_for_status()

            access_token = auth_response.json().get(
                "access_token"
            )

            if not access_token:

                payment.status = "FAILED"
                payment.result_description = (
                    "Could not obtain M-Pesa access token."
                )
                payment.save()

                return Response(
                    {
                        "error": "Could not obtain M-Pesa access token."
                    },
                    status=status.HTTP_502_BAD_GATEWAY
                )

        except requests.RequestException as error:

            payment.status = "FAILED"
            payment.result_description = str(error)
            payment.save()

            return Response(
                {
                    "error": "Failed to connect to M-Pesa.",
                    "details": str(error),
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        # ----------------------------------------------------
        # TIMESTAMP
        # ----------------------------------------------------

        timestamp = datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )

        # ----------------------------------------------------
        # PASSWORD
        # ----------------------------------------------------

        password_string = (
            settings.MPESA_BUSINESS_SHORT_CODE
            + settings.MPESA_PASSKEY
            + timestamp
        )

        password = base64.b64encode(
            password_string.encode()
        ).decode()

        # ----------------------------------------------------
        # STK PUSH PAYLOAD
        # ----------------------------------------------------

        stk_url = (
            "https://sandbox.safaricom.co.ke/"
            "mpesa/stkpush/v1/processrequest"
        )

        payload = {

            "BusinessShortCode":
                settings.MPESA_BUSINESS_SHORT_CODE,

            "Password":
                password,

            "Timestamp":
                timestamp,

            "TransactionType":
                "CustomerPayBillOnline",

            "Amount":
                int(float(amount)),

            "PartyA":
                phone_number,

            "PartyB":
                settings.MPESA_BUSINESS_SHORT_CODE,

            "PhoneNumber":
                phone_number,

            "CallBackURL":
                settings.MPESA_CALLBACK_URL,

            "AccountReference":
                account_reference,

            "TransactionDesc":
                description,
        }

        print("STK PAYLOAD:", payload)

        headers = {
            "Authorization":
                f"Bearer {access_token}",

            "Content-Type":
                "application/json",
        }

        # ----------------------------------------------------
        # SEND STK PUSH
        # ----------------------------------------------------

        try:

            response = requests.post(
                stk_url,
                json=payload,
                headers=headers,
                timeout=30,
            )

            data = response.json()

            print("M-PESA RESPONSE:", data)

            # ------------------------------------------------
            # SAVE M-PESA IDs
            # ------------------------------------------------

            payment.merchant_request_id = data.get(
                "MerchantRequestID"
            )

            payment.checkout_request_id = data.get(
                "CheckoutRequestID"
            )

            payment.result_code = data.get(
                "ResponseCode"
            )

            payment.result_description = data.get(
                "ResponseDescription"
            )

            if data.get("ResponseCode") != "0":

                payment.status = "FAILED"

            payment.save()

            # ------------------------------------------------
            # RETURN RESPONSE TO REACT
            # ------------------------------------------------

            return Response(
                {
                    "success":
                        data.get("ResponseCode") == "0",

                    "message":
                        data.get(
                            "CustomerMessage",
                            "M-Pesa request sent."
                        ),

                    "order_id":
                        order.id,

                    "payment_id":
                        payment.id,

                    "checkout_request_id":
                        payment.checkout_request_id,

                    "merchant_request_id":
                        payment.merchant_request_id,

                    "response":
                        data,
                },
                status=response.status_code,
            )

        except requests.RequestException as error:

            payment.status = "FAILED"
            payment.result_description = str(error)
            payment.save()

            print("M-PESA REQUEST FAILED:", error)

            return Response(
                {
                    "error":
                        "M-Pesa STK Push request failed.",

                    "details":
                        str(error),
                },
                status=status.HTTP_502_BAD_GATEWAY
            )


# ============================================================
# M-PESA CALLBACK
# ============================================================

class MpesaCallbackView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        print("\n========================================")
        print("M-PESA CALLBACK RECEIVED")
        print("========================================")

        print("CALLBACK DATA:")
        print(request.data)

        try:

            stk_callback = (
                request.data
                .get("Body", {})
                .get("stkCallback", {})
            )

            checkout_request_id = (
                stk_callback
                .get("CheckoutRequestID")
            )

            result_code = stk_callback.get(
                "ResultCode"
            )

            result_description = stk_callback.get(
                "ResultDesc"
            )

            print(
                "CHECKOUT REQUEST ID:",
                checkout_request_id
            )

            print(
                "RESULT CODE:",
                result_code
            )

            print(
                "RESULT DESCRIPTION:",
                result_description
            )

            # ------------------------------------------------
            # FIND PAYMENT
            # ------------------------------------------------

            try:

                payment = Payment.objects.get(
                    checkout_request_id=
                    checkout_request_id
                )

            except Payment.DoesNotExist:

                print(
                    "PAYMENT NOT FOUND:",
                    checkout_request_id
                )

                return Response(
                    {
                        "ResultCode": 0,
                        "ResultDesc":
                            "Accepted"
                    },
                    status=status.HTTP_200_OK
                )

            # ------------------------------------------------
            # SAVE RESULT
            # ------------------------------------------------

            payment.result_code = result_code
            payment.result_description = (
                result_description
            )

            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            if result_code == 0:

                payment.status = "SUCCESS"

                # --------------------------------------------
                # GET M-PESA RECEIPT
                # --------------------------------------------

                callback_metadata = (
                    stk_callback
                    .get("CallbackMetadata", {})
                    .get("Item", [])
                )

                for item in callback_metadata:

                    if item.get("Name") == (
                        "MpesaReceiptNumber"
                    ):

                        payment.mpesa_receipt_number = (
                            item.get("Value")
                        )

                # --------------------------------------------
                # COMPLETE ORDER
                # --------------------------------------------

                order = payment.order

                order.complete = True

                order.transaction_id = (
                    payment.mpesa_receipt_number
                )

                order.save()

                print(
                    "PAYMENT SUCCESSFUL!"
                )

                print(
                    "ORDER COMPLETED:",
                    order.id
                )

                print(
                    "PRODUCTS PAID FOR:"
                )

                for item in order.orderitems.all():

                    if item.product:

                        print(
                            f"- {item.product.name} "
                            f"x {item.quantity}"
                        )

            # ------------------------------------------------
            # FAILED
            # ------------------------------------------------

            else:

                payment.status = "FAILED"

            payment.save()

            return Response(
                {
                    "ResultCode": 0,
                    "ResultDesc": "Accepted"
                },
                status=status.HTTP_200_OK
            )

        except Exception as error:

            print(
                "CALLBACK ERROR:",
                error
            )

            return Response(
                {
                    "ResultCode": 0,
                    "ResultDesc": "Accepted"
                },
                status=status.HTTP_200_OK
            )