from django.urls import path

from .views import (
    PaymentTestView,
    MpesaSTKPushView,
    MpesaCallbackView,
)


urlpatterns = [

    # Test payment endpoint
    path(
        "test/",
        PaymentTestView.as_view(),
        name="payment-test"
    ),

    # M-Pesa STK Push
    path(
        "mpesa/stk-push/",
        MpesaSTKPushView.as_view(),
        name="mpesa-stk-push"
    ),

    # M-Pesa Callback
    path(
        "mpesa/callback/",
        MpesaCallbackView.as_view(),
        name="mpesa-callback"
    ),
]
