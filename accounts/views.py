from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView

from .forms import UserRegistrationForm, UserAddressForm
from .models import Customer, UserBankAccount

User = get_user_model()


# ----------------------------------
# USER REGISTRATION (eBanking)
# ----------------------------------
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

            # create customer profile only (NO account auto creation)
            Customer.objects.get_or_create(user=user)

            messages.success(
                request,
                "Account Created successfully. Please login to continue."
            )

            # IMPORTANT: do NOT auto login
            return redirect('accounts:user_login')

        return render(
            request,
            self.template_name,
            {
                'registration_form': registration_form,
                'address_form': address_form,
            }
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['registration_form'] = UserRegistrationForm()
        context['address_form'] = UserAddressForm()
        return context


# ----------------------------------
# LOGIN
# ----------------------------------
class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('accounts:dashboard')


# ----------------------------------
# LOGOUT
# ----------------------------------
class LogoutView(RedirectView):
    pattern_name = 'home'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


# ----------------------------------
# DASHBOARD (Logged-in user only)
# ----------------------------------
@login_required
def dashboard(request):
    account = UserBankAccount.objects.filter(user=request.user).first()

    if not account:
        messages.info(
            request,
            "No bank account found for your profile."
        )
        return redirect('accounts:account_list')

    recent_transactions = account.transactions.order_by('-timestamp')[:5]

    return render(
        request,
        'accounts/dashboard.html',
        {
            'account': account,
            'transactions': recent_transactions,
        }
    )


# ----------------------------------
# VIEW ALL ACCOUNTS (CORE MODULE)
# ----------------------------------
@login_required
def account_list(request):
    """
    CORE REQUIREMENT:
    View Accounts - List ALL accounts with balances
    """

    accounts = UserBankAccount.objects.select_related(
        'user',
        'account_type',
        'user__customer'
    ).all()

    return render(
        request,
        'accounts/account_list.html',
        {
            'accounts': accounts,
        }
    )


# ----------------------------------
# CREATE CUSTOMER (CORE – optional)
# ----------------------------------
@login_required
def create_customer(request):
    if request.method == 'POST':
        customer, created = Customer.objects.get_or_create(
            user=request.user
        )

        if created:
            messages.success(request, "Customer profile created")
        else:
            messages.info(request, "Customer profile already exists")

        return redirect('accounts:dashboard')

    return render(request, 'accounts/customer_form.html')
