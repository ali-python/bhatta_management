from django import forms
from .models import BrickEmployee, BrickAdvance, BrickSaving, BrickPayment, BrickLoan


class BrickEmployeeForm(forms.ModelForm):
    class Meta:
        model = BrickEmployee
        fields = ["name", "rate_per_1000"]

        labels = {
            "name": "مزدور کا نام",
            "rate_per_1000": "ریٹ فی ہزار اینٹ",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set default value
        self.fields["rate_per_1000"].initial = 1000

        # styling
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control",
                "style": "max-width:300px;"
            })


class BrickAdvanceForm(forms.ModelForm):
    class Meta:
        model = BrickAdvance
        fields = ["employee", "amount"]

        labels = {
            "employee": "مزدور",
            "amount": "ایڈوانس رقم",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control",
                "style": "max-width:300px;"
            })


class BrickSavingForm(forms.ModelForm):
    class Meta:
        model = BrickSaving
        fields = ["employee", "amount"]

        labels = {
            "employee": "مزدور",
            "amount": "جمع شدہ رقم",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control",
                "style": "max-width:300px;"
            })


class BrickPaymentForm(forms.ModelForm):
    class Meta:
        model = BrickPayment
        fields = ["amount"]

        labels = {
            "amount": "ادائیگی کی رقم",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["amount"].widget.attrs.update({
            "class": "form-control",
            "style": "max-width:300px;"
        })


class BrickLoanForm(forms.ModelForm):
    class Meta:
        model = BrickLoan
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
