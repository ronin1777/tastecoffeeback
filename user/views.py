from random import randint
from django.conf import settings
from django.http import JsonResponse, Http404
from django.utils.decorators import method_decorator

from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

import redis
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited

from kavenegar import *
from rest_framework_simplejwt.views import TokenRefreshView

from .models import OTP, User
from .permissions import IsOwner
from .serializers import OTPSerializer, UserRegistrationSerializer, PhoneNumberSerializer, \
    UserUpdateSerializer, UserRetrieveSerializer
import logging

from orders.models import Cart

logger = logging.getLogger(__name__)
KAVENEGAR_API_KEY = '4C704D6A52324844577148424A3733377A704263503141436E5075455759332F6F704238694F2F78525A773D'

redis_instance = redis.StrictRedis(host='a382f1fb-2baa-466d-8d0e-ca4bfe39e1b0.hsvc.ir', port=32371, db=1, password='JNXUmTdiGFZ5gUTlk2GSe8nGMvvtXLwF')


# class SendOtpView(generics.GenericAPIView):
#     serializer_class = OtpSerializer
#
#     def post(self, request, *args, **kwargs):
#         phone_number = request.data.get('phone_number')
#         request.session['phone_number'] = phone_number
#
#         otp_code = randint(100000, 999999)
#         otp = OTP.objects.create(phone_number=phone_number, otp_code=otp_code)
#         # Send OTP via SMS service (e.g., Kavenegar)
#         # try:
#         #     api = KavenegarAPI(
#         #         '4C704D6A52324844577148424A3733377A704263503141436E5075455759332F6F704238694F2F78525A773D')
#         #     params = {
#         #         'sender': '',  # optional
#         #         'receptor': phone_number,  # multiple mobile number, split by comma
#         #         'message': f"سلام به سایت tasetcoffee خوش امدید.\nرمز یک بار مصرف: {otp_code} ",
#         #     }
#         #     response = api.sms_send(params)
#         #     print(response)
#         # except APIException as e:
#         #     print(e)
#         # except HTTPException as e:
#         #     print(e)
#
#         return Response({"message": "OTP sent"}, status=status.HTTP_200_OK)


class SendOtpView(generics.GenericAPIView):
    serializer_class = PhoneNumberSerializer

    @method_decorator(ratelimit(key='post:phone_number', rate='20/m', method='POST', block=True))
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')

        if not phone_number:
            return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

        otp_code = randint(1000, 9999)

        redis_instance.setex(f"otp_{phone_number}", 600, otp_code)

        redis_instance.setex("current_phone_number", 600, phone_number)

        print(f"Stored OTP for {phone_number}: {otp_code}")  # برای دیباگ

        return Response({"message": f"OTP {otp_code} sent to {phone_number}"}, status=status.HTTP_200_OK)

    def handle_exception(self, exc):

        if isinstance(exc, Ratelimited):
            return JsonResponse({"error": "شما نمی‌توانید بیشتر از یک بار در دقیقه درخواست ارسال کنید."}, status=403)
        return super().handle_exception(exc)


class VerifyOtpView(generics.GenericAPIView):
    serializer_class = OTPSerializer

    def post(self, request, *args, **kwargs):
        global user_cart_data
        entered_otp = request.data.get('otp')
        phone_number = redis_instance.get("current_phone_number")
        phone_number_str = phone_number.decode() if phone_number else None
        saved_otp = redis_instance.get(f"otp_{phone_number_str}")

        if str(entered_otp) != str(saved_otp.decode('utf-8')):
            return Response({"error": "invalid"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(phone_number=phone_number_str)

        if created:
            return Response({"message": "register"}, status=status.HTTP_201_CREATED)

        if user:

            if not user.name or not user.email:
                return Response({"message": "کاربر جدید، لطفاً ثبت‌نام را تکمیل کنید"}, status=status.HTTP_202_ACCEPTED)
            else:

                refresh = RefreshToken.for_user(user)
                redis_instance.delete(f"otp_{phone_number_str}")
                user_cart = Cart.objects.filter(user=user).first()
                cart_exists = False
                if user_cart:
                    cart_exists = True

                return Response({
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "cartExists": cart_exists,
                }, status=status.HTTP_200_OK)


class CompleteRegistrationView(generics.GenericAPIView):
    serializer_class = UserRegistrationSerializer

    def patch(self, request, *args, **kwargs):
        phone_number = redis_instance.get("current_phone_number")
        phone_number_str = phone_number.decode() if phone_number else None
        name = request.data.get('name')
        email = request.data.get('email')

        try:
            user = User.objects.get(phone_number=phone_number_str)

            if user.name and user.email:
                return Response({"error": "شما قبلا ثبت نام کرده اید"}, status=status.HTTP_400_BAD_REQUEST)

            # به روز رسانی اطلاعات کاربر
            user.name = name if name else user.name
            user.email = email if email else user.email
            user.save()

            refresh = RefreshToken.for_user(user)
            redis_instance.delete(f"otp_{phone_number_str}")
            return Response({
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class UserRetrieveView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserRetrieveSerializer
    permission_classes = [IsAuthenticated]  # تغییر به IsAuthenticated

    def get_object(self):
        user = self.request.user

        # چک کردن اینکه کاربر احراز هویت شده است
        if user.is_authenticated:
            return user
        else:
            # مدیریت خطا برای کاربر غیر احراز هویت
            raise Http404("کاربر پیدا نشد.")


class UserProfileUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsOwner]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# npm warn ERESOLVE overriding peer dependency
# npm warn While resolving: airbnb-prop-types@2.16.0
# npm warn Found: react@18.3.1
# npm warn node_modules/react
# npm warn   peer react@">=16.8.0" from @emotion/react@11.13.3
# npm warn   node_modules/@emotion/react
# npm warn     peer @emotion/react@"^11.0.0-rc.0" from @emotion/styled@11.13.0
# npm warn     node_modules/@emotion/styled
# npm warn     4 more (@mui/material, @mui/styled-engine, @mui/system, the root project)
# npm warn   22 more (@emotion/styled, ...)
# npm warn
# npm warn Could not resolve dependency:
# npm warn peer react@"^0.14 || ^15.0.0 || ^16.0.0-alpha" from airbnb-prop-types@2.16.0
# npm warn node_modules/airbnb-prop-types
# npm warn   airbnb-prop-types@"^2.16.0" from react-with-direction@1.4.0
# npm warn   node_modules/react-with-direction
# npm warn   1 more (react-with-styles)
# npm warn
# npm warn Conflicting peer dependency: react@16.14.0
# npm warn node_modules/react
# npm warn   peer react@"^0.14 || ^15.0.0 || ^16.0.0-alpha" from airbnb-prop-types@2.16.0
# npm warn   node_modules/airbnb-prop-types
# npm warn     airbnb-prop-types@"^2.16.0" from react-with-direction@1.4.0
# npm warn     node_modules/react-with-direction
# npm warn     1 more (react-with-styles)
# npm error code ERESOLVE
# npm error ERESOLVE could not resolve
# npm error
# npm error While resolving: react-datepicker2@3.3.13
# npm error Found: react@18.3.1
# npm error node_modules/react
# npm error   peer react@">=16.8.0" from @emotion/react@11.13.3
# npm error   node_modules/@emotion/react
# npm error     peer @emotion/react@"^11.0.0-rc.0" from @emotion/styled@11.13.0
# npm error     node_modules/@emotion/styled
# npm error       peerOptional @emotion/styled@"^11.3.0" from @mui/material@6.1.2
# npm error       node_modules/@mui/material
# npm error         @mui/material@"^6.1.2" from the root project
# npm error       3 more (@mui/styled-engine, @mui/system, the root project)
# npm error     peerOptional @emotion/react@"^11.5.0" from @mui/material@6.1.2
# npm error     node_modules/@mui/material
# npm error       @mui/material@"^6.1.2" from the root project
# npm error     3 more (@mui/styled-engine, @mui/system, the root project)
# npm error   peer react@">=16.8.0" from @emotion/styled@11.13.0
# npm error   node_modules/@emotion/styled
# npm error     peerOptional @emotion/styled@"^11.3.0" from @mui/material@6.1.2
# npm error     node_modules/@mui/material
# npm error       @mui/material@"^6.1.2" from the root project
# npm error     peerOptional @emotion/styled@"^11.3.0" from @mui/styled-engine@6.1.2
# npm error     node_modules/@mui/styled-engine
# npm error       @mui/styled-engine@"^6.1.2" from @mui/system@6.1.2
# npm error       node_modules/@mui/system
# npm error         @mui/system@"^6.1.2" from @mui/material@6.1.2
# npm error         node_modules/@mui/material
# npm error     2 more (@mui/system, the root project)
# npm error   21 more (@emotion/use-insertion-effect-with-fallbacks, ...)
# npm error
# npm error Could not resolve dependency:
# npm error peer react@"^16.0.0" from react-datepicker2@3.3.13
# npm error node_modules/react-datepicker2
# npm error   react-datepicker2@"^3.3.13" from the root project
# npm error
# npm error Conflicting peer dependency: react@16.14.0
# npm error node_modules/react
# npm error   peer react@"^16.0.0" from react-datepicker2@3.3.13
# npm error   node_modules/react-datepicker2
# npm error     react-datepicker2@"^3.3.13" from the root project
# npm error
# npm error Fix the upstream dependency conflict, or retry
# npm error this command with --force or --legacy-peer-deps
# npm error to accept an incorrect (and potentially broken) dependency resolution.
# npm error
# npm error
# npm error For a full report see:
# npm error /home/comiser/.npm/_logs/2024-10-06T10_00_04_330Z-eresolve-report.txt
#
# npm error A complete log of this run can be found in: /home/comiser/.npm/_logs/2024-10-06T10_00_04_330Z-debug-0.log
