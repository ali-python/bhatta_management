from django.db import models
from django.utils import timezone

class HourlyEmployee(models.Model):
    name = models.CharField(max_length=200)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=100)

    def __str__(self):
        return self.name


class HourEntry(models.Model):
    employee = models.ForeignKey(HourlyEmployee, on_delete=models.CASCADE)
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.name} - {self.date}"


class HourlyAdvance(models.Model):
    employee = models.ForeignKey(HourlyEmployee, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Advance {self.amount} for {self.employee.name}"


class HourlySaving(models.Model):
    employee = models.ForeignKey(HourlyEmployee, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Saving {self.amount} for {self.employee.name}"


class HourlyPayment(models.Model):
    employee = models.ForeignKey(HourlyEmployee, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Payment {self.amount} to {self.employee.name}"


class HourlyLoan(models.Model):
    employee = models.ForeignKey(HourlyEmployee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    note = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.employee.name} - Loan ₹{self.amount}"

class HourlyAdvanceDeduction(models.Model):
    employee = models.ForeignKey(HourlyEmployee, on_delete=models.CASCADE)
    payment = models.ForeignKey(HourlyPayment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
