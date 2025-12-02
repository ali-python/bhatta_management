from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta, datetime, date
from collections import defaultdict
from .models import HourlyEmployee, HourEntry, HourlyAdvance, HourlySaving, HourlyPayment, HourlyLoan, HourlyAdvanceDeduction
from .forms import HourlyEmployeeForm, HourlyAdvanceForm, HourlySavingForm, HourlyLoanForm
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from decimal import Decimal

from decimal import Decimal, ROUND_HALF_UP

def hourly_dashboard(request):
    # Week navigation
    week_offset = int(request.GET.get("week", 0))
    today = timezone.now().date() + timedelta(days=7 * week_offset)

    # --- Week starts on SATURDAY ---
    weekday = today.weekday()            # Mon=0 … Sun=6
    days_since_saturday = (weekday - 5) % 7
    week_start = today - timedelta(days=days_since_saturday)
    week_dates = [week_start + timedelta(days=i) for i in range(7)]

    prev_week = week_offset - 1
    next_week = week_offset + 1

    employees = HourlyEmployee.objects.all().order_by("name")

    # --- Add new employee ---
    if request.method == "POST" and "add_employee" in request.POST:
        form = HourlyEmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("hourly:employees_dashboard")

    # --- Update hours (hours + minutes) ---
    if request.method == "POST" and "update_hours" in request.POST:
        for key, value in request.POST.items():
            if "_h" in key and key.startswith("hours_"):
                _, emp_id, date_str, _ = key.split("_")
                date = datetime.strptime(date_str, "%Y-%m-%d").date()

                hours = Decimal(value or 0)

                minutes_key = f"hours_{emp_id}_{date_str}_m"
                minutes = Decimal(request.POST.get(minutes_key, 0) or 0)

                # Convert minutes to decimal hours
                total_hours = hours + (minutes / Decimal(60))

                # Ensure very accurate rounding
                total_hours = total_hours.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

                entry, created = HourEntry.objects.get_or_create(
                    employee_id=emp_id,
                    date=date,
                )
                entry.hours = total_hours
                entry.save()

        return redirect(f"/hourly/employee/?week={week_offset}")

    # --- Build table data ---
    table = []

    for emp in employees:

        # FILTER weekly records
        week_hours = HourEntry.objects.filter(employee=emp, date__in=week_dates)
        week_payments = HourlyPayment.objects.filter(employee=emp, date__in=week_dates)
        week_advance_taken = HourlyAdvance.objects.filter(employee=emp, date__in=week_dates)
        week_advance_deducted = HourlyAdvanceDeduction.objects.filter(employee=emp, date__in=week_dates)

        # SUM only weekly amounts
        paid = sum(p.amount for p in week_payments)
        advance_taken = sum(a.amount for a in week_advance_taken)
        advance_deducted = sum(d.amount for d in week_advance_deducted)

        # Only savings & loan are lifetime, not weekly
        total_loan = sum(l.amount for l in HourlyLoan.objects.filter(employee=emp))
        saving = sum(s.amount for s in HourlySaving.objects.filter(employee=emp))

        total_hours = Decimal("0")

        row = {
            "employee": emp,
            "days": [],
            "total": 0,
            "total_hours": 0,

            # Weekly values
            "advance_taken": advance_taken,
            "advance_deducted": advance_deducted,
            "advance": advance_taken - advance_deducted,

            # Lifetime values
            "total_loan": total_loan,
            "saving": saving,

            # Weekly payment
            "paid": paid,
        }

        # --- DAILY HOURS ---
        for d in week_dates:
            entry = week_hours.filter(date=d).first()
            hours_decimal = entry.hours if entry else Decimal("0")
            hours_decimal = hours_decimal.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

            whole_hours = int(hours_decimal)
            minutes = int(((hours_decimal - Decimal(whole_hours)) * 60).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

            if minutes == 60:
                whole_hours += 1
                minutes = 0

            total_hours += hours_decimal
            amount = hours_decimal * emp.hourly_rate

            row["days"].append({
                "date": d,
                "hours": whole_hours,
                "minutes": minutes,
                "amount": amount,
            })

            row["total"] += amount

        row["total_hours"] = total_hours

        # --- Correct Weekly Remaining ---
        row["remaining"] = row["total"] - paid - advance_deducted - saving

        table.append(row)



    return render(request, "hourly_employee/hourly_dashboard.html", {
        "week_dates": week_dates,
        "table": table,
        "form": HourlyEmployeeForm(),
        "prev_week": prev_week,
        "next_week": next_week,
        "week_offset": week_offset,
    })



def add_advance(request):
    if request.method == "POST":
        form = HourlyAdvanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("hourly:employees_dashboard")

    return render(request, "hourly_employee/advance_form.html", {
        "form": HourlyAdvanceForm()
    })


def add_saving(request):
    if request.method == "POST":
        form = HourlySavingForm(request.POST)
        if form.is_valid():
            form.save()
            
            return redirect("hourly:employees_dashboard")

    return render(request, "hourly_employee/saving_form.html", {
        "form": HourlySavingForm()
    })


def give_payment(request, emp_id):
    emp = HourlyEmployee.objects.get(id=emp_id)

    total_hours_amount = sum(
        entry.hours * emp.hourly_rate
        for entry in HourEntry.objects.filter(employee=emp)
    )

    total_advance = sum(a.amount for a in HourlyAdvance.objects.filter(employee=emp))
    total_deducted = sum(d.amount for d in HourlyAdvanceDeduction.objects.filter(employee=emp))
    saving = sum(s.amount for s in HourlySaving.objects.filter(employee=emp))
    paid = sum(p.amount for p in HourlyPayment.objects.filter(employee=emp))

    remaining_advance = total_advance - total_deducted

    remaining = total_hours_amount - paid - remaining_advance - saving

    if request.method == "POST":
        amount = Decimal(request.POST.get("amount", "0"))
        if amount > 0:
            payment = HourlyPayment.objects.create(employee=emp, amount=amount)

            # deduct advance first
            if remaining_advance > 0:
                deduct = min(amount, remaining_advance)

                HourlyAdvanceDeduction.objects.create(
                    employee=emp,
                    payment=payment,
                    amount=deduct
                )
                payment.save()

        return redirect("hourly:employees_dashboard")

    return render(request, "hourly_employee/payment_confirm.html", {
        "employee": emp,
        "remaining": remaining
    })






def get_week_dates(offset=0):
    today = date.today()

    weekday = today.weekday()  # Monday=0 ... Sunday=6
    days_since_saturday = (weekday - 5) % 7

    this_week_saturday = today - timedelta(days=days_since_saturday)

    start_date = this_week_saturday + timedelta(weeks=offset)

    return [start_date + timedelta(days=i) for i in range(7)]


def employee_detail(request, emp_id):
    employee = get_object_or_404(HourlyEmployee, id=emp_id)
    week_offset = int(request.GET.get("week", 0))
    today = timezone.now().date() + timedelta(days=7 * week_offset)

    # --- Week start Saturday ---
    weekday = today.weekday()
    days_since_saturday = (weekday - 5) % 7
    week_start = today - timedelta(days=days_since_saturday)
    week_dates = [week_start + timedelta(days=i) for i in range(7)]

    days = []
    weekly_total = Decimal("0")

    for d in week_dates:
        entry = HourEntry.objects.filter(employee=employee, date=d).first()
        hours_decimal = Decimal(entry.hours) if entry else Decimal("0")
        amount = hours_decimal * Decimal(employee.hourly_rate)
        weekly_total += amount

        hours_int = int(hours_decimal)
        minutes_int = int(round((hours_decimal - hours_int) * 60))

        days.append({
            "date": d,
            "hours_decimal": hours_decimal,
            "hours": hours_int,
            "minutes": minutes_int,
            "amount": amount,
        })

    # All-time totals for summary
    total_saving  = sum(s.amount for s in HourlySaving.objects.filter(employee=employee))
    total_loan    = sum(l.amount for l in HourlyLoan.objects.filter(employee=employee))

    # Week-specific payments and advances
    weekly_paid = sum(
        p.amount for p in HourlyPayment.objects.filter(employee=employee, date__range=(week_dates[0], week_dates[-1]))
    )
    weekly_advance_deducted = sum(
        d.amount for d in HourlyAdvanceDeduction.objects.filter(employee=employee, payment__date__range=(week_dates[0], week_dates[-1]))
    )

    # Remaining for the week (cannot be negative)
    remaining = weekly_total - weekly_paid - weekly_advance_deducted - total_saving
    if remaining < 0:
        remaining = Decimal("0")

    # All-time histories
    payments = HourlyPayment.objects.filter(employee=employee).order_by("-date")
    advances = HourlyAdvance.objects.filter(employee=employee).order_by("-date")
    savings  = HourlySaving.objects.filter(employee=employee).order_by("-date")
    loans    = HourlyLoan.objects.filter(employee=employee).order_by("-date")

    return render(request, "hourly_employee/employee_detail.html", {
        "employee": employee,
        "week_dates": week_dates,
        "prev_week": week_offset - 1,
        "next_week": week_offset + 1,
        "days": days,
        "weekly_total": weekly_total,
        "weekly_paid": weekly_paid,
        "weekly_advance_deducted": weekly_advance_deducted,
        "total_saving": total_saving,
        "total_loan": total_loan,
        "remaining": remaining,
        "payments": payments,
        "advances": advances,
        "savings": savings,
        "loans": loans,
    })

def add_loan(request):
    if request.method == "POST":
        form = HourlyLoanForm(request.POST)
        if form.is_valid():
            loan = form.save()
            return redirect("hourly:employees_dashboard")
    else:
        form = HourlyLoanForm()

    return render(request, "hourly_employee/add_loan.html", {"form": form})
