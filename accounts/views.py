from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import HttpResponseRedirect, redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView

from .forms import UserRegistrationForm, UserAddressForm
from .models import UserBankAccount

User = get_user_model()


# -------------------------
# USER REGISTRATION
# -------------------------
class UserRegistrationView(TemplateView):
    template_name = 'accounts/user_registration.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        registration_form = UserRegistrationForm(request.POST)
        address_form = UserAddressForm(request.POST)

        if registration_form.is_valid() and address_form.is_valid():
            user = registration_form.save()

            address = address_form.save(commit=False)
            address.user = user
            address.save()

            login(request, user)
            messages.success(
                request,
                f'Account created successfully. '
                f'Your Account Number is {user.account.account_no}'
            )
            return redirect('accounts:dashboard')

        return render(
            request,
            self.template_name,
            {
                'registration_form': registration_form,
                'address_form': address_form
            }
        )


# -------------------------
# LOGIN / LOGOUT
# -------------------------
class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    redirect_authenticated_user = True


class LogoutView(RedirectView):
    pattern_name = 'home'

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            logout(self.request)
        return super().get_redirect_url(*args, **kwargs)


# -------------------------
# DASHBOARD
# -------------------------
@login_required
def dashboard(request):
    account = request.user.account
    recent_transactions = account.transactions.order_by('-timestamp')[:5]

    return render(request, 'accounts/dashboard.html', {
        'account': account,
        'transactions': recent_transactions
    })


# -------------------------
# ACCOUNT LIST (CORE MODULE)
# -------------------------
@login_required
def account_list(request):
    accounts = UserBankAccount.objects.filter(user=request.user)
    return render(request, 'accounts/account_list.html', {
        'accounts': accounts
    })
