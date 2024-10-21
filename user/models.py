from datetime import timedelta, datetime
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import AbstractBaseUser

from .managers import UserManager


class User(AbstractBaseUser):
    phone_number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    bio = models.TextField(max_length=500, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def has_perm(self, perm, obj=None):
        """
        این متد بررسی می‌کند که آیا کاربر مجوز خاصی دارد یا خیر.
        """
        return True

    def has_module_perms(self, app_label):
        """
        این متد بررسی می‌کند که آیا کاربر مجوز دسترسی به اپلیکیشنی خاص را دارد یا خیر.
        """
        return True

    @property
    def is_superuser(self):
        """
        این متد بررسی می‌کند که آیا کاربر ادمین است یا خیر.
        """
        return self.is_admin

    def __str__(self):
        return self.phone_number

    class Meta:
        verbose_name = _('کاربر')
        verbose_name_plural = _('کاربر ها')


class OTP(models.Model):
    phone_number = models.CharField(max_length=11, unique=True)
    otp_code = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now=True)

    def is_valid(self):
        """
        این متد بررسی می‌کند که آیا OTP هنوز معتبر است یا خیر.
        """
        return self.created_at >= timezone.now() - timedelta(minutes=10)

    def __str__(self):
        return f'{self.phone_number} - {self.otp_code} - {self.created_at}'

