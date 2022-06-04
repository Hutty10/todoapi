import threading

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import EmailMessage
from rest_framework_simplejwt.tokens import RefreshToken


# Create your models here.

class EmailThreading(threading.Thread):

    def __init__(self, email) -> None:
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class UserManager(BaseUserManager):

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Users must have an email address'))
        if not username:
            raise ValueError(_('User must have username'))
        if password is None:
            raise ValueError(_('Users must have a Password'))
        user = self.model(email=self.normalize_email(email), username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        if not extra_fields.get('is_staff'):
             raise ValueError(_('staff must be set to true'))
        if not extra_fields.get('is_superuser'):
            raise ValueError(_('Superuser must be set to true'))
        user = self.create_user(email, username, password, **extra_fields)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(verbose_name=_('Username'), max_length=50, unique=True, db_index=True)
    email = models.EmailField(verbose_name=_("Email address"), max_length=254, unique=True, db_index=True)
    img = models.ImageField(verbose_name=_('Profile image'), upload_to='profile_img/', default='profile_img/default.png', blank=True)

    is_active = models.BooleanField(default=True) # to activate and deactivate the account
    is_verified = models.BooleanField(default=False)
    # add admin control or not
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
                }

    def send_email(self, email_subject, email_body):
        email = EmailMessage(subject=email_subject, body=email_body, to=[self.email])
        # email.send()
        EmailThreading(email).start()

    def __str__(self) -> str:
        return self.username

