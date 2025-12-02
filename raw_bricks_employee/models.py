from django.db import models
from django.utils import timezone
from decimal import Decimal

class BrickEmployee(models.Model):
    name = models.CharField(max_length=100)
    rate_per_1000 = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class BrickWorkEntry(models.Model):
    employee = models.ForeignKey(BrickEmployee, on_delete=models.CASCADE)
    date = models.DateField()
    bricks_count = models.IntegerField(default=0)

    def amount(self):
        return Decimal(self.bricks_count) * Decimal(self.employee.rate_per_1000) / Decimal('1000')


class BrickAdvance(models.Model):
    employee = models.ForeignKey(BrickEmployee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)



class BrickSaving(models.Model):
    employee = models.ForeignKey(BrickEmployee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)


class BrickPayment(models.Model):
    employee = models.ForeignKey(BrickEmployee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)

class BrickLoan(models.Model):
    employee = models.ForeignKey(BrickEmployee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    note = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.employee.name} - Loan ₹{self.amount}"

class BrickAdvanceDeduction(models.Model):
    employee = models.ForeignKey(BrickEmployee, on_delete=models.CASCADE)
    payment = models.ForeignKey(BrickPayment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True) 