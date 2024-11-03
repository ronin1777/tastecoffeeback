from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken

import logging
import requests
from rest_framework_simplejwt.tokens import AccessToken

from orders.models import Order
from payment.models import Payment
from payment.zarinnpal import Zarinpal
from tastecofee.settings import CALLBACK_URL, FRONT_URL, ZARINPAL_MERCHANT_ID, ADMIN_PHONE_NUMBER
from user.utils import send_sms_to_admin

logger = logging.getLogger(__name__)




class ZarinpalPaymentRequestView(APIView):
    def post(self, request):
        order_id = request.data.get('order_id')
        order = get_object_or_404(Order, id=order_id)

        amount = int(order.final_price)
        description = f"پرداخت آزمایشی برای سفارش {order_id}"[:500]
        callback_url = f"{CALLBACK_URL}/api/payment/callback-verify/"

        zarinpal = Zarinpal(merchant_id=f'{ZARINPAL_MERCHANT_ID}', debug=True)

        try:

            result = zarinpal.payment_gateway(
                amount=amount,
                callback_url=callback_url,
                description=description,
            )

            if result['status']:

                Payment.objects.create(
                    order=order,
                    authority=result['authority'],
                    amount=amount,
                    status='initiated'
                )
                return Response({"payment_url": result['url']}, status=status.HTTP_200_OK)

            return Response({"error": result['errors']}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ZarinpalCallbackView(APIView):
    def get(self, request):
        authority = request.GET.get('Authority')
        status_param = request.GET.get('Status')

        if not authority or not status_param:
            return Response({"error": "Authority یا Status وجود ندارد."}, status=status.HTTP_400_BAD_REQUEST)

        payment = Payment.objects.filter(authority=authority).first()

        if not payment:
            return Response({"error": "پرداختی با این Authority پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)

        amount = payment.amount
        zarinpal = Zarinpal(merchant_id=f'{ZARINPAL_MERCHANT_ID}', debug=True)


        user = payment.order.user


        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)


        if status_param == "OK":
            try:
                verification_result = zarinpal.verify_payment(authority=authority, amount=amount)

                if verification_result['status']:
                    payment.ref_id = verification_result.get('ref_id', None)
                    payment.status = 'successful'
                    payment.save()

                    order = payment.order
                    order.complete_order()
                    send_sms_to_admin(admin_phone=ADMIN_PHONE_NUMBER, user_phone=user.phone_number, user_name=user.name)
                    response = JsonResponse({"success": True})


                    response['Location'] = f"{FRONT_URL}/payment/success?ref_id={verification_result.get('ref_id', '')}&amount={amount}&status=successful"
                    response.status_code = 302
                    return response

                else:
                    payment.status = 'failed'
                    payment.save()

                    response = JsonResponse({"success": False})

                    return redirect(f"{FRONT_URL}/payment/failure?error=Payment%20failed&status=failed")

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:

            payment.status = 'failed'
            payment.save()


            response = JsonResponse({"success": False})

            return redirect(f"{FRONT_URL}/payment/failure?error=Payment%20failed&status=failed")


# class ZarinpalPaymentRequestView(APIView):
#     def post(self, request, *args, **kwargs):
#         # نمونه داده برای تست
#         amount = 1000  # مبلغ به ریال
#         order_id = request.data.get('order_id', 1)  # شناسه سفارش (برای تست)
#
#         data = {
#             'MerchantID': 'YOUR_MERCHANT_ID',  # مرچنت آی‌دی تست
#             'Amount': amount,
#             'Description': f'پرداخت سفارش شماره {order_id}',
#             'CallbackURL': 'http://localhost:8000/payment/verify/',  # آدرس لوکال
#         }
#
#         response = requests.post(
#             'https://sandbox.zarinpal.com/pg/v4/payment/request.json',
#             headers={'Content-Type': 'application/json'},
#             json=data
#         )
#
#         if response.status_code == 200:
#             json_response = response.json()
#             if json_response['Status'] == 100:
#                 return Response(
#                     {"payment_url": f"https://sandbox.zarinpal.com/pg/StartPay/{json_response['Authority']}"}
#                 )
#             else:
#                 return Response({"error": "Error in request payment."}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response({"error": "Failed to connect to payment gateway.", "details": response.json()},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#
# class ZarinpalPaymentVerifyView(APIView):
#     def get(self, request, *args, **kwargs):
#         authority = request.GET.get('Authority')
#         order_id = request.GET.get('order_id', 1)
#
#         data = {
#             'MerchantID': 'YOUR_MERCHANT_ID',  # مرچنت آی‌دی
#             'Authority': authority,
#             'Amount': 1000,  # مبلغ به ریال
#         }
#
#         response = requests.post('https://sandbox.zarinpal.com/pg/v4/payment/verification.json', json=data)
#
#         if response.status_code == 200:
#             json_response = response.json()
#             if json_response['Status'] == 100:
#                 return Response({"message": "Payment was successful", "RefID": json_response['RefID']})
#             else:
#                 return Response({"error": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)
#         return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)