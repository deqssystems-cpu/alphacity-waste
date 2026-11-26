import csv
from datetime import date
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .forms import ExpenseForm, ClientForm, PaymentForm, BinForm, EnquiryForm
from .images import IMAGES
from .models import Expense, Client, Payment, BinSupply, Enquiry, SERVICES

def htmx(r):
    return r.headers.get("HX-Request") == "true"

def home(request):
    return render(request, "core/home.html", {"form": EnquiryForm(), "img": IMAGES})

@require_POST
def enquiry(request):
    f = EnquiryForm(request.POST)
    if f.is_valid():
        f.save()
        return render(request, "core/partials/enquiry_done.html")
    return render(request, "core/partials/enquiry_form.html", {"form": f})

@login_required
def dashboard(request):
    first = date.today().replace(day=1)
    active = Client.objects.filter(active=True)
    paid_ids = Payment.objects.filter(month=first).values_list("client_id", flat=True)
    unpaid = active.exclude(id__in=paid_ids)
    exp = Expense.objects.filter(date__year=first.year, date__month=first.month)
    spent = exp.aggregate(s=Sum("amount"))["s"] or 0
    collected = Payment.objects.filter(month=first).aggregate(s=Sum("amount"))["s"] or 0
    ctx = {
        "spent": spent, "net": collected - spent, "img": IMAGES, "recent_exp": exp[:5],
        "total": Client.objects.count(), "active_count": active.count(),
        "collected": Payment.objects.filter(month=first).aggregate(s=Sum("amount"))["s"] or 0,
        "expected": active.aggregate(s=Sum("monthly_fee"))["s"] or 0,
        "unpaid": unpaid[:8], "unpaid_count": unpaid.count(),
        "new_enquiries": Enquiry.objects.filter(handled=False).count(),
        "by_service": [(l, active.filter(service=k).count()) for k, l in SERVICES],
        "recent": Payment.objects.select_related("client")[:6], "month": first,
    }
    return render(request, "core/dashboard.html", ctx)

@login_required
def client_list(request):
    qs = Client.objects.all()
    q, s = request.GET.get("q", ""), request.GET.get("service", "")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(phone__icontains=q) | Q(estate__icontains=q))
    if s:
        qs = qs.filter(service=s)
    ctx = {"clients": qs, "q": q, "service": s, "services": SERVICES}
    return render(request, "core/partials/client_rows.html" if htmx(request) else "core/clients.html", ctx)

@login_required
def client_edit(request, pk=None):
    obj = get_object_or_404(Client, pk=pk) if pk else None
    form = ClientForm(request.POST or None, instance=obj)
    if form.is_valid():
        c = form.save()
        return redirect("client_detail", pk=c.pk)
    return render(request, "core/client_form.html", {"form": form, "obj": obj})

def _detail_ctx(c, **extra):
    return {"c": c, "payments": c.payments.all(), "bins": c.bins.all(), **extra}

@login_required
def client_detail(request, pk):
    c = get_object_or_404(Client, pk=pk)
    return render(request, "core/client_detail.html", _detail_ctx(
        c, pform=PaymentForm(initial={"month": date.today(), "amount": c.monthly_fee}), bform=BinForm()))

@login_required
@require_POST
def payment_add(request, pk):
    c = get_object_or_404(Client, pk=pk)
    f = PaymentForm(request.POST)
    if f.is_valid():
        p = f.save(commit=False); p.client = c; p.save()
        f = PaymentForm(initial={"month": date.today(), "amount": c.monthly_fee})
    return render(request, "core/partials/payments_block.html", _detail_ctx(c, pform=f))

@login_required
@require_POST
def payment_delete(request, pk):
    p = get_object_or_404(Payment, pk=pk); c = p.client; p.delete()
    return render(request, "core/partials/payments_block.html", _detail_ctx(
        c, pform=PaymentForm(initial={"month": date.today(), "amount": c.monthly_fee})))

@login_required
@require_POST
def bin_add(request, pk):
    c = get_object_or_404(Client, pk=pk)
    f = BinForm(request.POST)
    if f.is_valid():
        b = f.save(commit=False); b.client = c; b.save(); f = BinForm()
    return render(request, "core/partials/bins_block.html", _detail_ctx(c, bform=f))

@login_required
def payments(request):
    month = request.GET.get("month") or date.today().strftime("%Y-%m")
    y, m = map(int, month.split("-"))
    first = date(y, m, 1)
    paid = Payment.objects.filter(month=first).select_related("client")
    unpaid = Client.objects.filter(active=True).exclude(id__in=paid.values_list("client_id", flat=True))
    ctx = {"paid": paid, "unpaid": unpaid, "month": month, "total": paid.aggregate(s=Sum("amount"))["s"] or 0}
    return render(request, "core/payments.html", ctx)

@login_required
def enquiries(request):
    return render(request, "core/enquiries.html", {"items": Enquiry.objects.all()})

@login_required
@require_POST
def enquiry_toggle(request, pk):
    e = get_object_or_404(Enquiry, pk=pk); e.handled = not e.handled; e.save()
    return render(request, "core/partials/enquiry_row.html", {"e": e})


def _ym(request):
    m = request.GET.get("month") or date.today().strftime("%Y-%m")
    y, mo = map(int, m.split("-"))
    return m, y, mo

@login_required
def expenses(request):
    month, y, mo = _ym(request)
    form = ExpenseForm(initial={"date": date.today()})
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            form = ExpenseForm(initial={"date": date.today()})
    qs = Expense.objects.filter(date__year=y, date__month=mo)
    cats = dict(Expense.CATEGORIES)
    by_cat = [(cats[r["category"]], r["t"]) for r in qs.values("category").annotate(t=Sum("amount")).order_by("-t")]
    ctx = {"form": form, "items": qs, "month": month, "total": qs.aggregate(s=Sum("amount"))["s"] or 0, "by_cat": by_cat}
    return render(request, "core/partials/expenses_block.html" if htmx(request) else "core/expenses.html", ctx)

@login_required
@require_POST
def expense_delete(request, pk):
    get_object_or_404(Expense, pk=pk).delete()
    return redirect("expenses")

@login_required
def reports(request):
    t, rows = date.today(), []
    for i in range(5, -1, -1):
        y, mo = t.year, t.month - i
        while mo < 1:
            mo += 12; y -= 1
        inc = Payment.objects.filter(month=date(y, mo, 1)).aggregate(s=Sum("amount"))["s"] or 0
        out = Expense.objects.filter(date__year=y, date__month=mo).aggregate(s=Sum("amount"))["s"] or 0
        rows.append({"label": date(y, mo, 1), "inc": inc, "out": out, "net": inc - out})
    top = max([max(r["inc"], r["out"]) for r in rows] + [1])
    for r in rows:
        r["ip"], r["op"] = int(r["inc"] * 100 / top), int(r["out"] * 100 / top)
    owing = sorted([c for c in Client.objects.filter(active=True) if c.balance > 0], key=lambda c: -c.balance)[:10]
    return render(request, "core/reports.html", {"rows": rows, "owing": owing,
        "tin": sum(r["inc"] for r in rows), "tout": sum(r["out"] for r in rows), "tnet": sum(r["net"] for r in rows)})

@login_required
def receipt(request, pk):
    return render(request, "core/receipt.html", {"p": get_object_or_404(Payment, pk=pk)})

@login_required
def export_csv(request, kind):
    r = HttpResponse(content_type="text/csv")
    r["Content-Disposition"] = f'attachment; filename="alphacity_{kind}.csv"'
    w = csv.writer(r)
    if kind == "clients":
        w.writerow(["Name", "Phone", "Service", "Estate", "Monthly fee", "Paid", "Balance"])
        for c in Client.objects.all():
            w.writerow([c.name, c.phone, c.get_service_display(), c.estate, c.monthly_fee, c.total_paid, c.balance])
    elif kind == "expenses":
        w.writerow(["Date", "Category", "Description", "Paid to", "Amount"])
        for e in Expense.objects.all():
            w.writerow([e.date, e.get_category_display(), e.description, e.paid_to, e.amount])
    else:
        w.writerow(["Client", "Month", "Amount", "Method", "Reference", "Paid on"])
        for p in Payment.objects.select_related("client"):
            w.writerow([p.client.name, p.month, p.amount, p.get_method_display(), p.reference, p.paid_on])
    return r
