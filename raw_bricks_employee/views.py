from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta
from django.utils import timezone

from .models import (
    BrickEmployee, BrickWorkEntry, BrickAdvance, BrickSaving, BrickPayment, BrickLoan, BrickAdvanceDeduction
)
from .forms import (
    BrickEmployeeForm, BrickAdvanceForm, BrickSavingForm, BrickPaymentForm, BrickLoanForm
)
from decimal import Decimal
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, timedelta
from django.shortcuts import render, redirect
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


def bricks_dashboard(request):
    week_offset = int(request.GET.get("week", 0))
    week_dates = get_week_dates(week_offset)

    # Add new employee
    if request.method == "POST" and "add_employee" in request.POST:
        form = BrickEmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(f"/raw-brick-employee/dashboard/?week={week_offset}")
    else:
        form = BrickEmployeeForm()

    # Update bricks
    if request.method == "POST" and "update_bricks" in request.POST:
        for emp in BrickEmployee.objects.all():
            for d in week_dates:
                key = f"bricks_{emp.id}_{d}"
                value = request.POST.get(key, "")
                if value == "":
                    continue
                bricks = int(value)
                entry, created = BrickWorkEntry.objects.get_or_create(employee=emp, date=d)
                entry.bricks_count = bricks
                entry.save()

        return redirect(f"/raw-brick-employee/dashboard/?week={week_offset}")

    # Prepare weekly table
    table = []
    employees = BrickEmployee.objects.all()

    for emp in employees:
        days_list = []
        weekly_total = Decimal("0")
        weekly_bricks = 0

        for d in week_dates:
            work = BrickWorkEntry.objects.filter(employee=emp, date=d).first()
            bricks = work.bricks_count if work else 0
            amount = (Decimal(bricks) / Decimal(1000)) * Decimal(emp.rate_per_1000)

            weekly_total += amount
            weekly_bricks += bricks

            days_list.append({
                "date": d,
                "bricks": bricks,
                "amount": amount
            })

        # WEEK DATA ONLY
        advance = BrickAdvance.objects.filter(
            employee=emp, date__in=week_dates
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        advance_deduction = BrickAdvanceDeduction.objects.filter(
            employee=emp, date__in=week_dates
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        paid = BrickPayment.objects.filter(
            employee=emp, date__in=week_dates
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        # SAVING AND LOAN ARE LIFETIME (stay in next week)
        saving = BrickSaving.objects.filter(
            employee=emp
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        loan = BrickLoan.objects.filter(
            employee=emp
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        # Correct remaining (weekly only)
        remaining = weekly_total - advance - paid - saving 

        table.append({
            "employee": emp,
            "days": days_list,
            "total": weekly_total,
            "weekly_bricks": weekly_bricks,
            "advance": advance - advance_deduction,
            "saving": saving,
            "paid": paid,
            "loan": loan,
            "remaining": remaining
        })

    return render(request, "raw_brick_employee/brick_dashboard.html", {
        "week_dates": week_dates,
        "prev_week": week_offset - 1,
        "next_week": week_offset + 1,
        "table": table,
        "form": form,
    })




def update_bricks(request):
    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("bricks_"):
                _, emp_id, date_str = key.split("_")
                emp = BrickEmployee.objects.get(id=emp_id)

                entry, created = BrickWorkEntry.objects.get_or_create(
                    employee=emp,
                    date=date_str
                )
                entry.bricks_count = int(value or 0)
                entry.save()

    return redirect(request.META.get("HTTP_REFERER"))


def brick_employee_detail(request, emp_id):
    emp = get_object_or_404(BrickEmployee, id=emp_id)

    week_offset = int(request.GET.get("week", 0))
    week_dates = get_week_dates(week_offset)

    rows = []
    weekly_total = Decimal("0")

    for d in week_dates:
        entry, _ = BrickWorkEntry.objects.get_or_create(employee=emp, date=d)
        amount = Decimal(entry.amount())
        rows.append({
            "date": d,
            "bricks": entry.bricks_count,
            "amount": round(amount),
        })
        weekly_total += amount

    # All-time totals for summary
    total_saving = BrickSaving.objects.filter(employee=emp).aggregate(total=models.Sum("amount"))["total"] or Decimal("0")
    total_loan = BrickLoan.objects.filter(employee=emp).aggregate(total=models.Sum("amount"))["total"] or Decimal("0")

    # Week-specific payments and advance deductions
    weekly_paid = BrickPayment.objects.filter(employee=emp, date__range=(week_dates[0], week_dates[-1])).aggregate(total=models.Sum("amount"))["total"] or Decimal("0")
    weekly_advance_deducted = BrickAdvanceDeduction.objects.filter(employee=emp, payment__date__range=(week_dates[0], week_dates[-1])).aggregate(total=models.Sum("amount"))["total"] or Decimal("0")

    # Remaining for the week (cannot be negative)
    remaining = weekly_total - weekly_paid - weekly_advance_deducted - total_saving
    if remaining < 0:
        remaining = Decimal("0")

    return render(request, "raw_brick_employee/brick_employee_detail.html", {
        "employee": emp,
        "daily": rows,

        # histories
        "payments": BrickPayment.objects.filter(employee=emp).order_by("-date"),
        "advance": BrickAdvance.objects.filter(employee=emp).order_by("-date"),
        "saving": BrickSaving.objects.filter(employee=emp).order_by("-date"),
        "loans": BrickLoan.objects.filter(employee=emp).order_by("-date"),

        # summary card numbers
        "summary": {
            "total": weekly_total,
            "advance": total_saving,
            "saving": total_saving,
            "paid": weekly_paid,
            "loan": total_loan,
            "remaining": remaining,
            "remaing_loan" : total_loan - total_saving
        },

        "prev_week": week_offset - 1,
        "next_week": week_offset + 1,
    })



def add_brick_advance(request):
    if request.method == "POST":
        form = BrickAdvanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("raw_bricks_employee:dashboard")

    return render(request, "raw_brick_employee/brick_advance_form.html", {
        "form": BrickAdvanceForm()
    })



def add_brick_saving(request):
    if request.method == "POST":
        form = BrickSavingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("raw_bricks_employee:dashboard")

    return render(request, "raw_brick_employee/brick_saving_form.html", {
        "form": BrickSavingForm()
    })



def give_brick_payment(request, emp_id):
    emp = get_object_or_404(BrickEmployee, id=emp_id)

    # Calculate remaining advance
    total_advance = BrickAdvance.objects.filter(employee=emp).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.0')
    total_deducted = BrickAdvanceDeduction.objects.filter(employee=emp).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.0')
    remaining_advance = total_advance - total_deducted
    if request.method == "POST":
        form = BrickPaymentForm(request.POST)
        if form.is_valid():
            pay = form.save(commit=False)
            pay.employee = emp
            pay.save()

            # Deduct from remaining advance first
            if remaining_advance > 0:
                amount_due = pay.amount
                deduct_amount = min(amount_due, remaining_advance)
                print(deduct_amount)
                if deduct_amount > 0:
                    BrickAdvanceDeduction.objects.create(
                        employee=emp,
                        payment=pay,
                        amount=remaining_advance
                    )

            return redirect("raw_bricks_employee:employee_detail", emp_id)
    else:
        form = BrickPaymentForm()

    return render(request, "raw_brick_employee/brick_payment_form.html", {
        "form": form,
        "employee": emp,
        "remaining_advance": remaining_advance,
    })
def add_loan(request):
    if request.method == "POST":
        form = BrickLoanForm(request.POST)
        if form.is_valid():
            loan = form.save()


            return redirect("raw_bricks_employee:dashboard")
    else:
        form = BrickLoanForm()

    return render(request, "raw_brick_employee/add_loan.html", {"form": form})
