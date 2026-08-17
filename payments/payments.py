from django.urls import path

from .views import (
    MpesaSTKPushView,
    MpesaCallbackView
)


urlpatterns = [

    path(
        "stk-push/",
        MpesaSTKPushView.as_view(),
        name="mpesa-stk-push"
    ),

    path(
        "callback/",
        MpesaCallbackView.as_view(),
        name="mpesa-callback"
    ),

]