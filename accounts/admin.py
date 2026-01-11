from django.contrib import admin
from .models import User, Customer, UserBankAccount, BankAccountType, UserAddress

admin.site.register(User)
admin.site.register(Customer)
admin.site.register(UserBankAccount)
admin.site.register(BankAccountType)
admin.site.register(UserAddress)
