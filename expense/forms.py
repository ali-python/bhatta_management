from django import forms
from expense.models import Expense


class ExpenseFormView(forms.ModelForm):
    class Meta:
        model = Expense
        fields = '__all__'
