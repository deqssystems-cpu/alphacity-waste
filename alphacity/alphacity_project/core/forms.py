from django import forms
from .models import Client, Payment, BinSupply, Enquiry

class Styled(forms.ModelForm):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        for f in self.fields.values():
            f.widget.attrs.setdefault("class", "input")

class ClientForm(Styled):
    class Meta:
        model = Client
        fields = ["name", "phone", "email", "service", "estate", "address", "monthly_fee", "start_date", "active", "notes"]
        widgets = {"start_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"), "notes": forms.Textarea(attrs={"rows": 2})}

class PaymentForm(Styled):
    class Meta:
        model = Payment
        fields = ["month", "amount", "method", "reference", "paid_on"]
        widgets = {"month": forms.DateInput(attrs={"type": "date"}), "paid_on": forms.DateInput(attrs={"type": "date"})}

class BinForm(Styled):
    class Meta:
        model = BinSupply
        fields = ["size", "quantity", "price", "date"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}

class EnquiryForm(Styled):
    class Meta:
        model = Enquiry
        fields = ["name", "phone", "service", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 3})}

from .models import Expense

class ExpenseForm(Styled):
    class Meta:
        model = Expense
        fields = ["date", "category", "description", "paid_to", "amount"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}
