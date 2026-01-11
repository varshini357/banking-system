from django.urls import path   # ✅ THIS LINE WAS MISSING

from .views import (
    UserRegistrationView,
    LogoutView,
    UserLoginView,
    dashboard,
    account_list,
)

app_name = "accounts"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="user_login"),
    path("logout/", LogoutView.as_view(), name="user_logout"),
    path("register/", UserRegistrationView.as_view(), name="user_registration"),
    path("dashboard/", dashboard, name="dashboard"),
    path("accounts/", account_list, name="account_list"),
]
