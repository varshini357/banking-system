from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import GENDER_CHOICE
from .managers import UserManager


# -------------------------
# CUSTOM USER MODEL
# -------------------------
class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @property
    def balance(self):
        if hasattr(self, 'account'):
            return self.account.balance
        return 0


# -------------------------
# CUSTOMER MODEL
# -------------------------
class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer'
    )
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.email


# -------------------------
# BANK ACCOUNT TYPE
# -------------------------
class BankAccountType(models.Model):
    name = models.CharField(max_length=100)
    maximum_withdrawal_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return self.name


# -------------------------
# USER BANK ACCOUNT
# -------------------------
class UserBankAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='account',
        on_delete=models.CASCADE
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accounts'
    )
    account_type = models.ForeignKey(
        BankAccountType,
        on_delete=models.CASCADE
    )
    account_no = models.PositiveIntegerField(unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICE)
    birth_date = models.DateField(null=True, blank=True)
    balance = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return str(self.account_no)


# -------------------------
# USER ADDRESS
# -------------------------
class UserAddress(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='address',
        on_delete=models.CASCADE
    )
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.PositiveIntegerField()
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.user.email
