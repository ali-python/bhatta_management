from django.db import models
from django.utils import timezone

class KachiBrickEmployee(models.Model):
    name = models.CharField(max_length=100)
    rate_per_1000 = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class KachiBrickWorkEntry(models.Model):
    employee = models.ForeignKey(KachiBrickEmployee, on_delete=models.CASCADE)
    date = models.DateField()
    bricks_count = models.IntegerField(default=0)

    def amount(self):
        return (self.bricks_count / 1000) * float(self.employee.rate_per_1000)


class KachiBrickAdvance(models.Model):
    employee = models.ForeignKey(KachiBrickEmployee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)


class KachiBrickSaving(models.Model):
    employee = models.ForeignKey(KachiBrickEmployee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)


class KachiBrickPayment(models.Model):
    employee = models.ForeignKey(KachiBrickEmployee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)

class KachiBrickLoan(models.Model):
    employee = models.ForeignKey(KachiBrickEmployee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    note = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.employee.name} - Loan ₹{self.amount}"

class KachiBrickAdvanceDeduction(models.Model):
    employee = models.ForeignKey(KachiBrickEmployee, on_delete=models.CASCADE)
    payment = models.ForeignKey(KachiBrickPayment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)