from django import forms
from .models import *

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "phone", "address"]

        labels = {
            "name": "نام",
            "phone": "فون نمبر",
            "address": "پتہ",
        }

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "نام"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "فون نمبر"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "پتہ"}),
        }



class CustomerLedgerForm(forms.ModelForm):
    class Meta:
        model = CustomerLedger
        fields = ["amount_due", "paid", "detail", "date"]

        labels = {
            "amount_due": "بقایا رقم",
            "paid": "ادا شدہ رقم",
            "detail": "تفصیل",
            "date": "تاریخ",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control",
                "style": "max-width:300px;"
            })

class TractorTripForm(forms.ModelForm):
    class Meta:
        model = TractorTrip
        fields = [
            'customer', 'tractor', 'driver', 'conductor', 
            'date', 'bricks_carried', 'brick_type', 
            'brick_rate', 'trip_amount'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    # override required settings
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.required = False


class TractorPaymentForm(forms.ModelForm):
    class Meta:
        model = TractorPayment
        fields = ['employee', 'date', 'amount', 'remarks']

        labels = {
            'employee': 'ملازم',
            'date': 'تاریخ',
            'amount': 'رقم',
            'remarks': 'تفصیل',
        }

        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class CustomerPaymentForm(forms.ModelForm):
    class Meta:
        model = CustomerPayment
        fields = ["trip", "amount", "date"]
class CustomerAdvanceForm(forms.ModelForm):
    class Meta:
        model = CustomerAdvance
        fields = ['amount', 'date']  # remove customer from form

        labels = {
            'amount': 'رقم',
            'date': 'تاریخ',
        }

        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
        }


class TractorSavingForm(forms.ModelForm):
    class Meta:
        model = TractortSaving
        fields = ["employee", "amount"]

        labels = {
            "employee": "مزدور",
            "amount": "جمع کی گئی رقم",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control form-control-sm",
                "style": "max-width: 220px;"
            })


class TractorLoanForm(forms.ModelForm):
    class Meta:
        model = TractorLoan 
        fields = ["employee", "amount", "note"]

        labels = {
            "employee": "مزدور",
            "amount": "قرض کی رقم",
            "note": "تفصیل",
        }

        widgets = {
            "employee": forms.Select(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "note": forms.TextInput(attrs={"class": "form-control"}),
        }