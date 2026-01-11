from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import HttpResponseRedirect, redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView

from .forms import UserRegistrationForm, UserAddressForm
from .models import Customer, UserBankAccount  # ADD Customer import

User = get_user_model()

class UserRegistrationView(TemplateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/user_registration.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(
                reverse_lazy('transactions:transaction_report')
            )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        registration_form = UserRegistrationForm(self.request.POST)
        address_form = UserAddressForm(self.request.POST)

        if registration_form.is_valid() and address_form.is_valid():
            user = registration_form.save()
            address = address_form.save(commit=False)
            address.user = user
            address.save()

            login(self.request, user)
            messages.success(
                self.request,
                (
                    f'Thank You For Creating A Bank Account. '
                    f'Your Account Number is {user.account.account_no}. '
                )
            )
            return HttpResponseRedirect(
                reverse_lazy('transactions:deposit_money')
            )

        return self.render_to_response(
            self.get_context_data(
                registration_form=registration_form,
                address_form=address_form
            )
        )

    def get_context_data(self, **kwargs):
        if 'registration_form' not in kwargs:
            kwargs['registration_form'] = UserRegistrationForm()
        if 'address_form' not in kwargs:
            kwargs['address_form'] = UserAddressForm()

        return super().get_context_data(**kwargs)

class UserLoginView(LoginView):
    template_name='accounts/user_login.html'
    redirect_authenticated_user = True

class LogoutView(RedirectView):
    pattern_name = 'home'

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            logout(self.request)
        return super().get_redirect_url(*args, **kwargs)

# YOUR NEW CUSTOMER VIEW - PERFECTLY WORKING
@login_required
def create_customer(request):
    """Create customer profile for logged-in user"""
    if request.method == 'POST':
        user = request.user  # Current logged-in user
        customer, created = Customer.objects.get_or_create(user=user)
        if created:
            messages.success(request, '✅ Customer profile created successfully!')
        else:
            messages.info(request, 'ℹ️ Customer profile already exists!')
        return redirect('dashboard')  # or reverse_lazy('transactions:transaction_report')
    
    return render(request, 'accounts/customer_form.html')

# BONUS: Account List View (Your Core Module)
@login_required
def account_list(request):
    """List all accounts for current user"""
    user_accounts = UserBankAccount.objects.filter(user=request.user)
    return render(request, 'accounts/account_list.html', {
        'accounts': user_accounts
    })
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    account = request.user.account
    recent_transactions = account.transactions.order_by('-timestamp')[:5]

    return render(request, 'accounts/dashboard.html', {
        'account': account,
        'transactions': recent_transactions
    })
