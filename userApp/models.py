# models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, phone, first_name, last_name, role='user', password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, phone, first_name, last_name, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            role='admin',
            password=password
        )
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user
    
    
class CustomUser(AbstractBaseUser):
    USER_ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
        ('hr', 'Hr'),
    )

    first_name = models.CharField(max_length=30, default='')
    last_name = models.CharField(max_length=30, default='')
    username = models.CharField(unique=True, max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10, unique=True, null=True, blank=True)
    role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_superuser(self):
        return self.is_admin
