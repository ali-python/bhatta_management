from django import forms
from .models import*

class BrickOutSavingForm(forms.ModelForm):
    class Meta:
        model = BrickOutSaving
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


class BrickOutLoanForm(forms.ModelForm):
    class Meta:
        model = BrickOutLoan
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