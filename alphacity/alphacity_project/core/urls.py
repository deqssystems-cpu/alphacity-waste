from django.urls import path
from django.contrib.auth import views as auth
from . import views as v
from .images import IMAGES
urlpatterns = [
    path("", v.home, name="home"),
    path("enquiry/", v.enquiry, name="enquiry"),
    path("login/", auth.LoginView.as_view(template_name="core/login.html", extra_context={"img": IMAGES}), name="login"),
    path("logout/", auth.LogoutView.as_view(), name="logout"),
    path("dashboard/", v.dashboard, name="dashboard"),
    path("clients/", v.client_list, name="clients"),
    path("clients/new/", v.client_edit, name="client_new"),
    path("clients/<int:pk>/", v.client_detail, name="client_detail"),
    path("clients/<int:pk>/edit/", v.client_edit, name="client_edit"),
    path("clients/<int:pk>/payment/", v.payment_add, name="payment_add"),
    path("clients/<int:pk>/bins/", v.bin_add, name="bin_add"),
    path("payments/<int:pk>/delete/", v.payment_delete, name="payment_delete"),
    path("payments/", v.payments, name="payments"),
    path("expenses/", v.expenses, name="expenses"),
    path("expenses/<int:pk>/delete/", v.expense_delete, name="expense_delete"),
    path("reports/", v.reports, name="reports"),
    path("receipt/<int:pk>/", v.receipt, name="receipt"),
    path("export/<str:kind>/", v.export_csv, name="export"),
    path("enquiries/", v.enquiries, name="enquiries"),
    path("enquiries/<int:pk>/toggle/", v.enquiry_toggle, name="enquiry_toggle"),
]
