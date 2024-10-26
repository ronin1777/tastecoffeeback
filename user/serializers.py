from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=13)


class OTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=9)


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'email')

def validate_email(self, value):
    if User.objects.filter(email=value).exists():
        raise serializers.ValidationError("این ایمیل قبلاً استفاده شده است، لطفاً ایمیل دیگری وارد کنید.")
    return value



class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'name', 'email', 'bio', 'location', 'birth_date', 'postal_code',
                  'profile_picture']


class UserUpdateSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'bio', 'location',
                  'birth_date', 'profile_picture', 'postal_code', 'phone_number')

    def update(self, instance, validated_data):
        profile_picture = validated_data.pop('profile_picture', None)
        if profile_picture:
            instance.profile_picture = profile_picture

        return super().update(instance, validated_data)
