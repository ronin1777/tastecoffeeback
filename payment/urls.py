from django.urls import path

from payment.views import ZarinpalPaymentRequestView, ZarinpalCallbackView

app_name = 'payment'

urlpatterns = [
    path('payment/', ZarinpalPaymentRequestView.as_view(), name='payment-request'),
    path('callback-verify/', ZarinpalCallbackView.as_view(), name='verify_payment'),

]
