from django.db import models
from django.utils import timezone
from decimal import Decimal
from employee.models import Employee  

class Payment(models.Model):
    """Final or weekly payments made to employees."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.name} - ₹{self.amount} on {self.date}"

