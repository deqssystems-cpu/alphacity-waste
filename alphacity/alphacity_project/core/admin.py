from django.contrib import admin
from .models import Client, Payment, BinSupply, Enquiry, Expense
for m in (Client, Payment, BinSupply, Enquiry, Expense):
    admin.site.register(m)
