from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta
from django.utils import timezone

from .models import *
from kachi_ent_bharai.forms import *
from decimal import Decimal
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, timedelta
from django.db.models import Sum
import datetime

def get_week_dates(offset=0):
    today = datetime.date.today()

    # Calculate current week's Saturday
    weekday = today.weekday()  # Monday=0 … Sunday=6
    # We want: Saturday = 5
    days_since_saturday = (weekday - 5) % 7

    this_week_saturday = today - datetime.timedelta(days=days_since_saturday)

    # Apply week offset
    start_date = this_week_saturday + datetime.timedelta(weeks=offset)

    # Build full week: Saturday → Friday (7 days)
    return [start_date + datetime.timedelta(days=i) for i in range(7)]


def Kachi_bricks_dashboard(request):
    week_offset = int(request.GET.get("week", 0))
    week_dates = get_week_dates(week_offset)

    # --- Add Employee ---
    if request.method == "POST" and "add_employee" in request.POST:
        form = BrickEmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(f"/kachi/ent/bharai/dashboard/?week={week_offset}")
    else:
        form = BrickEmployeeForm()

    # --- Update Weekly Bricks ---
    if request.method == "POST" and "update_bricks" in request.POST:
        employees = KachiBrickEmployee.objects.all()
        for emp in employees:
            for d in week_dates:
                field = f"bricks_{emp.id}_{d}"
                value = request.POST.get(field)
                if value:
                    bricks = int(value)
                    work, _ = KachiBrickWorkEntry.objects.get_or_create(
                        employee=emp,
                        date=d
                    )
                    work.bricks_count = bricks
                    work.save()
        return redirect(f"/kachi/ent/bharai/dashboard/?week={week_offset}")

    # --- Prepare Table Data ---
    table = []
    employees = KachiBrickEmployee.objects.all()

    for emp in employees:
        days_list = []
        weekly_total_amount = Decimal("0")
        weekly_bricks = 0 

        # Daily entries
        for d in week_dates:
            work = KachiBrickWorkEntry.objects.filter(employee=emp, date=d).first()
            bricks = work.bricks_count if work else 0
            amount = Decimal(str(work.amount())) if work else Decimal("0")
            weekly_total_amount += amount
            weekly_bricks += bricks
            days_list.append({"date": d, "bricks": bricks, "amount": amount})

        # --- Weekly financials ---
        weekly_paid = KachiBrickPayment.objects.filter(
            employee=emp, date__in=week_dates
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        # All-time advance & deduction
        total_advance = KachiBrickAdvance.objects.filter(employee=emp).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        total_deduction = KachiBrickAdvanceDeduction.objects.filter(employee=emp).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        advance_remaining = total_advance - total_deduction
        if advance_remaining < 0:
            advance_remaining = Decimal("0")

        # Lifetime savings & loans
        saving_lifetime = KachiBrickSaving.objects.filter(employee=emp).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        loan_lifetime = KachiBrickLoan.objects.filter(employee=emp).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        # --- Correct remaining ---
        remaining = weekly_total_amount - weekly_paid - total_advance - saving_lifetime
        if remaining < 0:
            remaining = Decimal("0")

        table.append({
            "weekly_bricks": weekly_bricks,
            "employee": emp,
            "days": days_list,
            "total": weekly_total_amount,
            "advance": advance_remaining,
            "saving": saving_lifetime,
            "paid": weekly_paid,
            "loan": loan_lifetime,
            "deducted": total_deduction,
            "remaining": remaining
        })

    return render(request, "kachi_ent_bharai/kachi_ent_dashboard.html", {
        "week_dates": week_dates,
        "prev_week": week_offset - 1,
        "next_week": week_offset + 1,
        "table": table,
        "form": form
    })
def update_bricks(request):
    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("bricks_"):
                _, emp_id, date_str = key.split("_")
                emp = KachiBrickEmployee.objects.get(id=emp_id)

                entry, created = KachiBrickWorkEntry.objects.get_or_create(
                    employee=emp,
                    date=date_str
                )
                entry.bricks_count = int(value or 0)
                entry.save()

    return redirect(request.META.get("HTTP_REFERER"))


def brick_employee_detail(request, emp_id):
    emp = get_object_or_404(KachiBrickEmployee, id=emp_id)

    week_offset = int(request.GET.get("week", 0))
    week_dates = get_week_dates(week_offset)

    rows = []
    total = Decimal("0")
    for d in week_dates:
        entry, _ = KachiBrickWorkEntry.objects.get_or_create(employee=emp, date=d)
        amount = Decimal(entry.amount())  # convert float -> Decimal
        rows.append({
            "date": d,
            "bricks": entry.bricks_count,
            "amount": round(amount),
        })
        total += amount

    # Aggregations (all-time values for summary)
    advance = KachiBrickAdvance.objects.filter(employee=emp).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")
    advance_deducted = KachiBrickAdvanceDeduction.objects.filter(employee=emp).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")
    saving = KachiBrickSaving.objects.filter(employee=emp).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")
    loan = KachiBrickLoan.objects.filter(employee=emp).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")

    # Payments **only for the current week**
    # Payments only for the current week
    paid = KachiBrickPayment.objects.filter(
        employee=emp,
        date__range=(week_dates[0], week_dates[-1])
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    # Weekly advance deductions only
    weekly_advance_deducted = KachiBrickAdvanceDeduction.objects.filter(
        employee=emp,
        payment__date__range=(week_dates[0], week_dates[-1])
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    
    # Correct weekly remaining (never negative)
    remaining = total - paid - advance - saving
    if remaining < 0:
        remaining = Decimal("0")

    print(saving)
    return render(request, "kachi_ent_bharai/brick_employee_detail.html", {
        "employee": emp,
        "daily": rows,

        # histories
        "payments": KachiBrickPayment.objects.filter(employee=emp).order_by("-date"),
        "advance": KachiBrickAdvance.objects.filter(employee=emp).order_by("-date"),
        "saving": KachiBrickSaving.objects.filter(employee=emp).order_by("-date"),
        "loans": KachiBrickLoan.objects.filter(employee=emp).order_by("-date"),
        
        # summary card numbers
        "summary": {
            "total": total,
            "advance": advance,
            "saving": saving,
            "paid": paid,
            "loan": loan,
            "remaining": remaining,
            "remaing_loan" : loan - saving

        },

        "prev_week": week_offset - 1,
        "next_week": week_offset + 1,
    })

def add_brick_advance(request):
    if request.method == "POST":
        form = BrickAdvanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("kachi_ent_bharai:dashboard")

    return render(request, "kachi_ent_bharai/brick_advance_form.html", {
        "form": BrickAdvanceForm()
    })



def add_brick_saving(request):
    if request.method == "POST":
        form = BrickSavingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("kachi_ent_bharai:dashboard")

    return render(request, "kachi_ent_bharai/brick_saving_form.html", {
        "form": BrickSavingForm()
    })



def give_brick_payment(request, emp_id):
    emp = get_object_or_404(KachiBrickEmployee, id=emp_id)

    # Total advance taken by employee
    total_advance_taken = sum(a.amount for a in KachiBrickAdvance.objects.filter(employee=emp))

    # Total advance already deducted
    total_advance_deducted = sum(d.amount for d in KachiBrickAdvanceDeduction.objects.filter(employee=emp))

    # Pending advance (remaining to deduct)
    remaining_advance = total_advance_taken - total_advance_deducted

    if request.method == "POST":
        form = BrickPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.employee = emp
            payment.save()

            # Deduction amount = minimum of (payment.amount, remaining_advance)
            deduct_amount = min(payment.amount, remaining_advance)

            if deduct_amount > 0:
                KachiBrickAdvanceDeduction.objects.create(
                    employee=emp,
                    payment=payment,
                    amount=deduct_amount
                )

            return redirect("kachi_ent_bharai:employee_detail", emp_id)

    else:
        form = BrickPaymentForm()

    return render(request, "kachi_ent_bharai/brick_payment_form.html", {
        "form": form,
        "employee": emp,
        "remaining_advance": remaining_advance,
    })


def add_loan(request):
    if request.method == "POST":
        form = BrickLoanForm(request.POST)
        if form.is_valid():
            loan = form.save()
            return redirect("kachi_ent_bharai:dashboard")
    else:
        form = BrickLoanForm()

    return render(request, "kachi_ent_bharai/add_loan.html", {"form": form})
