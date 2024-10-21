from django.contrib.auth.models import BaseUserManager


# class UserManager(BaseUserManager):
#     def create_user(self, phone_number, name=None, email=None, password=None):
#         if not phone_number:
#             raise ValueError('Users must have a phone number')
#
#         if not name:
#             raise ValueError('Users must have a phone number')
#
#         if not email:
#             raise ValueError('Users must have a phone number')
#
#         user = self.model(phone_number=phone_number, name=name, email=email)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, phone_number, password=None):
#         user = self.create_user(phone_number=phone_number, password=password)
#         user.is_admin = True
#         user.save(using=self._db)
#         return user

class UserManager(BaseUserManager):
    def create_user(self, phone_number, name=None, email=None, password=None):
        if not phone_number:
            raise ValueError('Users must have a phone number')

        user = self.model(phone_number=phone_number, name=name, email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None):
        user = self.create_user(phone_number=phone_number, password=password)
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user
