from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Customer(models.Model):
    name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    date = models.DateField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_unpaid_amount(self):
        customer_ledgers = self.customer_ledger.all()

        if customer_ledgers:
            ledger_debit = customer_ledgers.aggregate(Sum('debit_amount'))
            ledger_credit = customer_ledgers.aggregate(Sum('credit_amount'))

            debit_amount = ledger_debit.get('debit_amount__sum')
            credit_amount = ledger_credit.get('credit_amount__sum')
        else:
            debit_amount = 0
            credit_amount = 0

        unpaid_amount = debit_amount - credit_amount
        return unpaid_amount


class CustomerLedger(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='customer_ledger'
    )
    invoice = models.ForeignKey(
        'sales.Invoice', related_name='invoice_ledger', blank=True, null=True, on_delete=models.CASCADE
    )
    debit_amount = models.DecimalField(
        max_digits=65, decimal_places=2, default=0, blank=True, null=True
    )
    credit_amount = models.DecimalField(
        max_digits=65, decimal_places=2, default=0, blank=True, null=True
    )
    details = models.TextField(max_length=500, blank=True, null=True)
    date = models.DateField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return self.customer.name
