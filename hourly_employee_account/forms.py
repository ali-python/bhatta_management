from django import forms
from .models import HourlyEmployee, HourlyAdvance, HourlySaving, HourlyLoan


class HourlyEmployeeForm(forms.ModelForm):
    class Meta:
        model = HourlyEmployee
        fields = ["name", "hourly_rate"]

        labels = {
            "name": "مزدور کا نام",
            "hourly_rate": "فی گھنٹہ مزدوری",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control form-control-sm",
                "style": "max-width: 220px;"
            })





class HourlyAdvanceForm(forms.ModelForm):
    class Meta:
        model = HourlyAdvance
        fields = ["employee", "amount"]

        labels = {
            "employee": "مزدور",
            "amount": "ایڈوانس رقم",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control form-control-sm",
                "style": "max-width: 220px;"
            })



class HourlySavingForm(forms.ModelForm):
    class Meta:
        model = HourlySaving
        fields = ["employee", "amount"]

        labels = {
            "employee": "مزدورv",
            "amount": "جمع کی گئی رقم",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control form-control-sm",
                "style": "max-width: 220px;"
            })


class HourlyLoanForm(forms.ModelForm):
    class Meta:
        model = HourlyLoan
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

