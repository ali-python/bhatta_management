from django.db import models
from django.utils import timezone


class Expense(models.Model):
    amount = models.DecimalField(max_digits=65, decimal_places=2, default=0,
                                 null=True, blank=True)
    description = models.TextField(max_length=500, null=True, blank=True)
    date = models.DateField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return str(self.amount)
