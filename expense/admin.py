from django.contrib import admin
from expense.models import Expense


class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'amount', 'description', 'date'
    )


admin.site.register(Expense, ExpenseAdmin)
