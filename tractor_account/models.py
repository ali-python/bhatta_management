from django.db import models
from django.utils import timezone
from decimal import Decimal

class TractorEmployee(models.Model):
    ROLE_CHOICES = [
        ('driver', 'Driver'),
        ('conductor', 'Conductor'),
    ]
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"

class Tractor(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class CustomerLedger(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    trip = models.ForeignKey('TractorTrip', on_delete=models.CASCADE, null=True, blank=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    detail = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now)
    class Meta:
        unique_together = ('customer', 'trip')  # prevents duplicates
class CustomerPayment(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    trip = models.ForeignKey('TractorTrip', on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    detail = models.TextField(null=True, blank=True)
    date = models.DateField(default=timezone.now)

BRICK_TYPE_CHOICES = [
    ('اَوّل', 'اَوّل'),
    ('بَیلی', 'بَیلی'),
    ('پکی بَیلی', 'پکی بَیلی'),
    ('کرڑی', 'کرڑی'),
    ('کھنگر', 'کھنگر'),
    ('ٹوٹا', 'ٹوٹا'),
    ('مِٹی', 'مِٹی'),
]

class TractorTrip(models.Model):
    customer = models.ForeignKey(
        'Customer', on_delete=models.CASCADE, related_name='tractor_trips', null=True, blank=True
    )
    tractor = models.ForeignKey(
        'Tractor', on_delete=models.CASCADE, related_name='trips'
    )
    date = models.DateField(default=timezone.now)
    driver = models.ForeignKey(
        'TractorEmployee', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='driver_trips', limit_choices_to={'role': 'driver'}
    )
    conductor = models.ForeignKey(
        'TractorEmployee', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='conductor_trips', limit_choices_to={'role': 'conductor'}
    )
    bricks_carried = models.IntegerField()
    brick_type = models.CharField(max_length=200, choices=BRICK_TYPE_CHOICES, default='A')
    brick_rate = models.DecimalField(max_digits=10, decimal_places=2, default=10)  # ₹ per brick
    trip_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Employee total split
    customer_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # auto calc

    def save(self, *args, **kwargs):
        # Only calculate customer amount
        self.customer_amount = Decimal(self.bricks_carried) * self.brick_rate
        super().save(*args, **kwargs)

    # Employee split
    def driver_share(self):
        if self.driver:
            if self.conductor:
                return self.trip_amount / 2
            return self.trip_amount  # full amount if no conductor
        return Decimal('0.0')

    def conductor_share(self):
        if self.conductor:
            return self.trip_amount / 2
        return Decimal('0.0')


    def __str__(self):
        return f"{self.tractor.name} - {self.bricks_carried} bricks ({self.brick_type}) on {self.date}"

class TractorAdvance(models.Model):
    employee = models.ForeignKey(TractorEmployee, on_delete=models.CASCADE, related_name='advances')
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Advance ₹{self.amount} to {self.employee.name} on {self.date}"

class TractorPayment(models.Model):
    employee = models.ForeignKey(TractorEmployee, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.employee.name} - ₹{self.amount} on {self.date}"

class CustomerAdvance(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    used_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def remaining_amount(self):
        return self.amount - self.used_amount

    def apply_amount(self, amount_to_apply: Decimal) -> Decimal:
        """
        Apply a given amount to this advance.
        Updates used_amount and saves immediately.
        Returns the amount actually applied.
        """
        remaining = self.remaining_amount
        applied = min(amount_to_apply, remaining)
        if applied > 0:
            self.used_amount += applied
            self.save(update_fields=['used_amount'])
        return applied

class TractorLoan(models.Model):
    employee = models.ForeignKey(TractorEmployee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    note = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.employee.name} - Loan ₹{self.amount}"


class TractortSaving(models.Model):
    employee = models.ForeignKey(TractorEmployee, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Saving {self.amount} for {self.employee.name}"