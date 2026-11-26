from datetime import date
from django.db import models
from django.db.models import Sum

SERVICES = [("residential", "Residential Garbage"), ("ewaste", "E-Waste"), ("liquid", "Liquid Waste")]

class Client(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    service = models.CharField(max_length=20, choices=SERVICES, default="residential")
    estate = models.CharField("Estate / Area", max_length=120, blank=True)
    address = models.CharField(max_length=200, blank=True)
    monthly_fee = models.DecimalField(max_digits=9, decimal_places=2, default=300)
    start_date = models.DateField(default=date.today)
    active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def months_billed(self):
        t = date.today()
        return max((t.year - self.start_date.year) * 12 + t.month - self.start_date.month + 1, 0)

    @property
    def total_paid(self):
        return self.payments.aggregate(s=Sum("amount"))["s"] or 0

    @property
    def balance(self):
        """Positive = client owes; negative = paid in advance."""
        return self.months_billed * self.monthly_fee - self.total_paid

    def paid_this_month(self):
        t = date.today().replace(day=1)
        return self.payments.filter(month=t).exists()


class Payment(models.Model):
    METHODS = [("mpesa", "M-Pesa"), ("cash", "Cash"), ("bank", "Bank")]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="payments")
    month = models.DateField("Month covered", help_text="Any date in the month being paid for")
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHODS, default="mpesa")
    reference = models.CharField("M-Pesa code / ref", max_length=40, blank=True)
    paid_on = models.DateField(default=date.today)

    class Meta:
        ordering = ["-month", "-paid_on"]

    def save(self, *a, **k):
        self.month = self.month.replace(day=1)
        super().save(*a, **k)


class BinSupply(models.Model):
    SIZES = [("60L", "60 Litre"), ("120L", "120 Litre"), ("240L", "240 Litre"), ("660L", "660 Litre")]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="bins")
    size = models.CharField(max_length=5, choices=SIZES, default="120L")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField("Total price", max_digits=9, decimal_places=2, default=0)
    date = models.DateField(default=date.today)

    class Meta:
        ordering = ["-date"]


class Enquiry(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    service = models.CharField(max_length=20, choices=SERVICES + [("bins", "Garbage Bins")])
    message = models.TextField(blank=True)
    handled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["handled", "-created"]


class Expense(models.Model):
    CATEGORIES = [("fuel", "Fuel"), ("salaries", "Salaries / wages"), ("repairs", "Vehicle repairs"),
                  ("bins", "Bins purchase"), ("dumping", "Dumping / disposal fees"), ("licence", "Licences & permits"),
                  ("airtime", "Airtime / internet"), ("other", "Other")]
    date = models.DateField(default=date.today)
    category = models.CharField(max_length=15, choices=CATEGORIES, default="fuel")
    description = models.CharField(max_length=200, blank=True)
    paid_to = models.CharField(max_length=120, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["-date", "-id"]
