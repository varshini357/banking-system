from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from accounts.models import UserBankAccount
from transactions.constants import DEPOSIT, WITHDRAWAL
from transactions.forms import (
    DepositForm,
    WithdrawForm,
    TransactionDateRangeForm,
    FundTransferForm,
)
from transactions.models import Transaction


# -------------------------
# TRANSACTION REPORT
# -------------------------
class TransactionRepostView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    form_data = {}

    def get(self, request, *args, **kwargs):
        form = TransactionDateRangeForm(request.GET or None)
        if form.is_valid():
            self.form_data = form.cleaned_data
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Transaction.objects.filter(
            account=self.request.user.account
        )

        daterange = self.form_data.get("daterange")
        if daterange:
            queryset = queryset.filter(timestamp__date__range=daterange)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account,
            'form': TransactionDateRangeForm(self.request.GET or None),
        })
        return context


# -------------------------
# BASE MIXIN
# -------------------------
class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    success_url = reverse_lazy('transactions:transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['account'] = self.request.user.account
        return kwargs


# -------------------------
# DEPOSIT
# -------------------------
class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm

    def get_initial(self):
        return {'transaction_type': DEPOSIT}

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        account = self.request.user.account

        account.balance += amount
        account.save(update_fields=['balance'])

        messages.success(self.request, f'{amount} credited successfully')
        return super().form_valid(form)


# -------------------------
# WITHDRAW
# -------------------------
class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm

    def get_initial(self):
        return {'transaction_type': WITHDRAWAL}

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        account = self.request.user.account

        account.balance -= amount
        account.save(update_fields=['balance'])

        messages.success(self.request, f'{amount} debited successfully')
        return super().form_valid(form)


# -------------------------
# FUND TRANSFER  ✅ MUST BE AT MODULE LEVEL
# -------------------------
@login_required
def fund_transfer(request):
    from_account = request.user.account

    if request.method == 'POST':
        form = FundTransferForm(request.POST, account=from_account)
        if form.is_valid():
            to_account_no = form.cleaned_data['to_account']
            amount = form.cleaned_data['amount']

            try:
                to_account = UserBankAccount.objects.get(
                    account_no=to_account_no
                )
            except UserBankAccount.DoesNotExist:
                messages.error(request, "Target account not found")
                return redirect('transactions:fund_transfer')

            # Debit
            from_account.balance -= amount
            from_account.save()

            Transaction.objects.create(
                account=from_account,
                amount=amount,
                balance_after_transaction=from_account.balance,
                transaction_type=WITHDRAWAL,
            )

            # Credit
            to_account.balance += amount
            to_account.save()

            Transaction.objects.create(
                account=to_account,
                amount=amount,
                balance_after_transaction=to_account.balance,
                transaction_type=DEPOSIT,
            )

            messages.success(request, "Fund transfer successful")
            return redirect('accounts:dashboard')

    else:
        form = FundTransferForm(account=from_account)

    return render(
        request,
        'transactions/fund_transfer.html',
        {'form': form},
    )
