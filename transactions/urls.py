from django.urls import path
from .views import (
    DepositMoneyView,
    WithdrawMoneyView,
    TransactionRepostView,
    fund_transfer,
)

app_name = "transactions"

urlpatterns = [
    path("deposit/", DepositMoneyView.as_view(), name="deposit_money"),
    path("withdraw/", WithdrawMoneyView.as_view(), name="withdraw_money"),
    path("report/", TransactionRepostView.as_view(), name="transaction_report"),
    path("transfer/", fund_transfer, name="fund_transfer"),
]
