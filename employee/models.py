from django.db import models
from decimal import Decimal

# Create your models here.

class Employee(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.name

    def get_total_work_amount(self):
        total = Decimal('0')
        for w in self.works.all():
            if w.rate:
                total += (Decimal(w.quantity) / Decimal('1000')) * w.rate.rate_per_1000
        return total

    # Total advance
    def get_total_advance(self):
        return sum((a.amount for a in self.advances.all()), Decimal('0'))

    # Total payments
    def get_total_paid(self):
        return sum((p.amount for p in self.payment_set.all()), Decimal('0'))

    def get_total_saving(self):
        return sum((s.amount for s in self.brickoutsaving_set.all()), Decimal('0'))
    # Unpaid = work - paid - advances
    def get_unpaid_amount(self):
        return self.get_total_work_amount() - self.get_total_paid() - self.get_total_advance() - self.get_total_saving()