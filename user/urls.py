from django.urls import path

from .views import SendOtpView, VerifyOtpView, CompleteRegistrationView, UserRetrieveView, UserProfileUpdateView


app_name = 'user'


urlpatterns = [
    path('send-otp/', SendOtpView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOtpView.as_view(), name='verify-otp'),
    path('complete-registration/', CompleteRegistrationView.as_view(), name='complete-registration'),
    path('user-profile/', UserRetrieveView.as_view(), name='user-profile'),
    path('user-update/', UserProfileUpdateView.as_view(), name='user-update'),

]
