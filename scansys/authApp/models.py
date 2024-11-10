from django.db import models
from enum import IntEnum
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager

class UserTypes(IntEnum):
  ADMIN = 1
  CLIENT = 2
  WAITER = 3

  @classmethod
  def choices(cls):
    return [(key.value, key.name) for key in cls]
  
class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, username=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        
        # Provide a default username if none is provided
        if username is None:
            username = email.split('@')[0]  # Or any other default logic you prefer

        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, username=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, username, **extra_fields)


class MyUser(AbstractUser):
  email = models.EmailField(unique=True)
  first_name = models.CharField(max_length=30, blank=True)
  type = models.IntegerField(choices=UserTypes.choices(), default=UserTypes.CLIENT)

  USERNAME_FIELD="email"
  REQUIRED_FIELDS=["username", "first_name"]

  objects = MyUserManager()
    
  def __str__(self) -> str:
    return self.email
  
