from random import randint
from django.conf import settings
from django.http import JsonResponse, Http404
from django.utils.decorators import method_decorator

from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


import redis
# from django_ratelimit.decorators import ratelimit
# from django_ratelimit.exceptions import Ratelimited

from kavenegar import *
from rest_framework_simplejwt.views import TokenRefreshView
from django.core.cache import cache

from .models import OTP, User
from .permissions import IsOwner
from .serializers import OTPSerializer, UserRegistrationSerializer, PhoneNumberSerializer, \
    UserUpdateSerializer, UserRetrieveSerializer
import logging

from orders.models import Cart

logger = logging.getLogger(__name__)
KAVENEGAR_API_KEY = '4C704D6A52324844577148424A3733377A704263503141436E5075455759332F6F704238694F2F78525A773D'

# redis_instance = redis.StrictRedis(host='a382f1fb-2baa-466d-8d0e-ca4bfe39e1b0.hsvc.ir', port=32371, db=1, password='JNXUmTdiGFZ5gUTlk2GSe8nGMvvtXLwF')


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


# class SendOtpView(generics.GenericAPIView):
    # serializer_class = PhoneNumberSerializer

    # @method_decorator(ratelimit(key='post:phone_number', rate='20/m', method='POST', block=True))
    # def post(self, request, *args, **kwargs):
    #     phone_number = request.data.get('phone_number')

    #     if not phone_number:
    #         return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

    #     otp_code = randint(1000, 9999)

    #     redis_instance.setex(f"otp_{phone_number}", 600, otp_code)

    #     redis_instance.setex("current_phone_number", 600, phone_number)

    #     print(f"Stored OTP for {phone_number}: {otp_code}")  # برای دیباگ

    #     return Response({"message": f"OTP {otp_code} sent to {phone_number}"}, status=status.HTTP_200_OK)

    # def handle_exception(self, exc):

    #     if isinstance(exc, Ratelimited):
    #         return JsonResponse({"error": "شما نمی‌توانید بیشتر از یک بار در دقیقه درخواست ارسال کنید."}, status=403)
    #     return super().handle_exception(exc)

class SendOtpView(generics.GenericAPIView):
    serializer_class = PhoneNumberSerializer
    throttle_classes = [AnonRateThrottle] 

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')

        if not phone_number:
            return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

        otp_code = randint(1000, 9999)

        # ذخیره OTP در کش
        cache.set(f"otp_{phone_number}", otp_code, timeout=600)
        cache.set("current_phone_number", phone_number, timeout=600)

        print(f"Stored OTP for {phone_number}: {otp_code}")  # برای دیباگ

        return Response({"message": f"OTP {otp_code} sent to {phone_number}"}, status=status.HTTP_200_OK)

    def handle_exception(self, exc):
        # بررسی خطای نرخ محدودسازی
        if isinstance(exc, Exception) and "throttled" in str(exc):
            return Response({"error": "شما نمی‌توانید بیشتر از 10 بار در دقیقه درخواست ارسال کنید."}, status=429)
        return super().handle_exception(exc)



class VerifyOtpView(generics.GenericAPIView):
    serializer_class = OTPSerializer

    def post(self, request, *args, **kwargs):
        entered_otp = request.data.get('otp')
        phone_number = cache.get("current_phone_number")  # استفاده از کش Django

        # نیازی به decode نیست، زیرا مقدار به عنوان str ذخیره شده است
        phone_number_str = phone_number if phone_number else None  
        saved_otp = cache.get(f"otp_{phone_number_str}")  # استفاده از کش Django

        if str(entered_otp) != str(saved_otp):
            return Response({"error": "invalid"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(phone_number=phone_number_str)

        if created:
            return Response({"message": "register"}, status=status.HTTP_201_CREATED)

        if user:
            if not user.name or not user.email:
                return Response({"message": "کاربر جدید، لطفاً ثبت‌نام را تکمیل کنید"}, status=status.HTTP_202_ACCEPTED)
            else:
                refresh = RefreshToken.for_user(user)
                cache.delete(f"otp_{phone_number_str}")  # استفاده از کش Django
                user_cart = Cart.objects.filter(user=user).first()
                cart_exists = user_cart is not None

                return Response({
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "cartExists": cart_exists,
                }, status=status.HTTP_200_OK)


class CompleteRegistrationView(generics.GenericAPIView):
    serializer_class = UserRegistrationSerializer

    def patch(self, request, *args, **kwargs):
        phone_number = cache.get("current_phone_number")
        phone_number_str = phone_number if phone_number else None
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
            cache.delete(f"otp_{phone_number_str}")
            return Response({
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)



# class VerifyOtpView(generics.GenericAPIView):
#     serializer_class = OTPSerializer

#     def post(self, request, *args, **kwargs):
#         global user_cart_data
#         entered_otp = request.data.get('otp')
#         phone_number = redis_instance.get("current_phone_number")
#         phone_number_str = phone_number.decode() if phone_number else None
#         saved_otp = redis_instance.get(f"otp_{phone_number_str}")

#         if str(entered_otp) != str(saved_otp.decode('utf-8')):
#             return Response({"error": "invalid"}, status=status.HTTP_400_BAD_REQUEST)

#         user, created = User.objects.get_or_create(phone_number=phone_number_str)

#         if created:
#             return Response({"message": "register"}, status=status.HTTP_201_CREATED)

#         if user:

#             if not user.name or not user.email:
#                 return Response({"message": "کاربر جدید، لطفاً ثبت‌نام را تکمیل کنید"}, status=status.HTTP_202_ACCEPTED)
#             else:

#                 refresh = RefreshToken.for_user(user)
#                 redis_instance.delete(f"otp_{phone_number_str}")
#                 user_cart = Cart.objects.filter(user=user).first()
#                 cart_exists = False
#                 if user_cart:
#                     cart_exists = True

#                 return Response({
#                     "access_token": str(refresh.access_token),
#                     "refresh_token": str(refresh),
#                     "cartExists": cart_exists,
#                 }, status=status.HTTP_200_OK)


# class CompleteRegistrationView(generics.GenericAPIView):
#     serializer_class = UserRegistrationSerializer

#     def patch(self, request, *args, **kwargs):
#         phone_number = redis_instance.get("current_phone_number")
#         phone_number_str = phone_number.decode() if phone_number else None
#         name = request.data.get('name')
#         email = request.data.get('email')

#         try:
#             user = User.objects.get(phone_number=phone_number_str)

#             if user.name and user.email:
#                 return Response({"error": "شما قبلا ثبت نام کرده اید"}, status=status.HTTP_400_BAD_REQUEST)

#             # به روز رسانی اطلاعات کاربر
#             user.name = name if name else user.name
#             user.email = email if email else user.email
#             user.save()

#             refresh = RefreshToken.for_user(user)
#             redis_instance.delete(f"otp_{phone_number_str}")
#             return Response({
#                 "access_token": str(refresh.access_token),
#                 "refresh_token": str(refresh)
#             }, status=status.HTTP_200_OK)

#         except User.DoesNotExist:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


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
