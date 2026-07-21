from django.urls import path
from .views import PaymentTestView

urlpatterns = [
    path('test/', PaymentTestView.as_view(), name='payment-test'),
]