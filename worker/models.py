from django.db import models
from django.utils import timezone

class Bhatta(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Worker(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    bhattas = models.ManyToManyField(Bhatta, related_name='workers')

    def __str__(self):
        return self.name


class WeeklyReport(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='weekly_reports')
    bhatta = models.ForeignKey(Bhatta, on_delete=models.CASCADE, related_name='weekly_reports')
    week_start = models.DateField()
    week_end = models.DateField()
    bricks_worked = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.worker.name} - {self.bhatta.name} ({self.week_start} to {self.week_end})"


class Advance(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='advances')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return f"{self.worker.name} - {self.amount}"


class Loan(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.worker.name} - {self.amount}"



class YearlySettlement(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='settlements')
    bhatta = models.ForeignKey(Bhatta, on_delete=models.CASCADE, related_name='settlements')
    year = models.IntegerField()
    brick_rate_per_1000 = models.DecimalField(max_digits=10, decimal_places=2)
    total_bricks = models.PositiveIntegerField()
    total_earned = models.DecimalField(max_digits=12, decimal_places=2)
    total_advance = models.DecimalField(max_digits=12, decimal_places=2)
    total_loan_deducted = models.DecimalField(max_digits=12, decimal_places=2)
    amount_to_pay = models.DecimalField(max_digits=12, decimal_places=2)
    payment_made = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    def __str__(self):
        return f"{self.worker.name} - {self.bhatta.name} ({self.year})"

class LoanDeduction(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='deductions')
    settlement = models.ForeignKey(YearlySettlement, on_delete=models.CASCADE, related_name='loan_deductions')
    deducted_amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Deducted {self.deducted_amount} from Loan {self.loan.id}"

class AdvanceDeduction(models.Model):
    advance = models.ForeignKey(Advance, related_name="deductions", on_delete=models.CASCADE)
    settlement = models.ForeignKey(YearlySettlement, related_name="advance_deductions", on_delete=models.CASCADE)
    deducted_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.deducted_amount} from {self.advance.worker.name}"
