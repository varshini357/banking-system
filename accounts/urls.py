from .views import UserRegistrationView, LogoutView, UserLoginView, dashboard

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="user_login"),
    path("logout/", LogoutView.as_view(), name="user_logout"),
    path("register/", UserRegistrationView.as_view(), name="user_registration"),
    path("dashboard/", dashboard, name="dashboard"),
]
from .views import account_list

path("accounts/", account_list, name="account_list"),
