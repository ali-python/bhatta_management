from django.db import models
from django.utils import timezone
from payment.models import Payment
from employee.models import Employee

class BrickRate(models.Model):
    """Rate per brick decided by the owner."""
    rate_per_1000 = models.DecimalField(max_digits=10, decimal_places=2, help_text="ہزار اِینٹوں کی قِیمت (in Rs)")
    effective_from = models.DateField(default=timezone.now)

    def __str__(self):
        return f"₹{self.rate_per_1000} ہزار اِینٹوں کی قِیمت (from {self.effective_from})"

class BrickWork(models.Model):
    """Record of how many bricks an employee brought."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='works')
    date = models.DateField(default=timezone.now)
    quantity = models.PositiveIntegerField(help_text="Number of bricks brought")
    brick_type = models.CharField(max_length=100, blank=True, null=True)
    rate = models.ForeignKey(BrickRate, on_delete=models.SET_NULL, null=True, blank=True)

    def calculate_amount(self):
        if self.rate:
            return (self.quantity / 1000) * float(self.rate.rate_per_1000)
        return 0

    def __str__(self):
        return f"{self.employee.name} - {self.quantity} bricks on {self.date}"


class AdvancePayment(models.Model):
    """Money given before weekly payment."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='advances')
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Advance ₹{self.amount} to {self.employee.name} on {self.date}"

class AdvanceDeduction(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="advance_deductions")
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="advance_deductions")
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Advance Deduction {self.amount} for {self.employee}"

class BrickOutLoan(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    note = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.employee.name} - Loan ₹{self.amount}"


class BrickOutSaving(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Saving {self.amount} for {self.employee.name}"