from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import BrickWork, AdvancePayment, BrickRate, AdvanceDeduction, BrickOutSaving, BrickOutLoan
from payment.models import Payment
from employee.models import Employee
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404, render
from django.db.models import Q

class BrickRateListView(ListView):
    model = BrickRate
    template_name = 'bricks_out/brickrate_list.html'


class BrickRateCreateView(CreateView):
    model = BrickRate
    fields = ['rate_per_1000', 'effective_from']
    template_name = 'bricks_out/brickrate_form.html'
    success_url = reverse_lazy('bricks_out:brickrate_list')

    def get_form(self):
        form = super().get_form()
        for field_name, field in form.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })
        return form


class BrickRateUpdateView(UpdateView):
    model = BrickRate
    fields = ['rate_per_1000', 'effective_from']
    template_name = 'bricks_out/brickrate_form.html'
    success_url = reverse_lazy('bricks_out:brickrate_list')

    def get_form(self):
        form = super().get_form()
        for field_name, field in form.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })
        return form

class BrickWorkListView(ListView):
    model = BrickWork
    template_name = 'bricks_out/brickwork_list.html'
    context_object_name = 'object_list'
    paginate_by = 10   # number of records per page
    ordering = '-id'
    def get_queryset(self):
        queryset = super().get_queryset().select_related('employee', 'rate')
        search = self.request.GET.get('search')

        if search:
            queryset = queryset.filter(
                employee__name__icontains=search
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context


from django import forms

class BrickWorkCreateView(CreateView):
    model = BrickWork
    fields = ['employee', 'date', 'quantity', 'rate', 'brick_type']
    template_name = 'bricks_out/brickwork_form.html'
    success_url = reverse_lazy('bricks_out:brickwork_list')
    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        form.fields['brick_type'].widget = forms.Select(
        choices=[
            ('اَوّل', 'اَوّل'),
            ('بَیلی', 'بَیلی'),
            ('پکی بَیلی', 'پکی بَیلی'),
            ('کرڑی', 'کرڑی'),
            ('کھنگر', 'کھنگر')
        ]
        )
        # Add Bootstrap classes
        form.fields['employee'].widget.attrs.update({'class': 'form-control form-select'})
        form.fields['date'].widget.attrs.update({'class': 'form-control'})
        form.fields['quantity'].widget.attrs.update({'class': 'form-control'})
        form.fields['rate'].widget.attrs.update({'class': 'form-control form-select'})
        form.fields['brick_type'].widget.attrs.update({'class': 'form-control form-select'})        # Auto-select latest BrickRate
        from .models import BrickRate
        latest_rate = BrickRate.objects.order_by('-effective_from').first()
        if latest_rate:
            form.fields['rate'].initial = latest_rate.id

        return form


class BrickWorkUpdateView(UpdateView):
    model = BrickWork
    fields = ['employee', 'date', 'quantity', 'rate']
    template_name = 'bricks_out/brickwork_form.html'
    success_url = reverse_lazy('bricks_out:brickwork_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Add Bootstrap classes
        form.fields['employee'].widget.attrs.update({'class': 'form-control form-select'})
        form.fields['date'].widget.attrs.update({'class': 'form-control'})
        form.fields['quantity'].widget.attrs.update({'class': 'form-control'})
        form.fields['rate'].widget.attrs.update({'class': 'form-control form-select'})

        return form


# --- AdvancePayment CRUD ---
class AdvanceListView(ListView):
    model = AdvancePayment
    template_name = 'bricks_out/advance_list.html'
    paginate_by = 10 
    ordering = '-id'

class AdvanceCreateView(CreateView):
    model = AdvancePayment
    fields = ['employee', 'date', 'amount']
    template_name = 'bricks_out/advance_form.html'
    success_url = reverse_lazy('bricks_out:advance_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Add Bootstrap classes
        form.fields['employee'].widget.attrs.update({'class': 'form-control form-select'})
        form.fields['date'].widget.attrs.update({'class': 'form-control'})
        form.fields['amount'].widget.attrs.update({'class': 'form-control'})

        return form


class AdvanceUpdateView(UpdateView):
    model = AdvancePayment
    fields = ['employee', 'date', 'amount']
    template_name = 'bricks_out/advance_form.html'
    success_url = reverse_lazy('bricks_out:advance_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Add Bootstrap classes
        form.fields['employee'].widget.attrs.update({'class': 'form-control form-select'})
        form.fields['date'].widget.attrs.update({'class': 'form-control'})
        form.fields['amount'].widget.attrs.update({'class': 'form-control'})

        return form


# --- Weekly Summary View ---
from decimal import Decimal
from django.utils import timezone

from datetime import timedelta
from django.utils import timezone
from decimal import Decimal

def weekly_summary(request):
    employees = Employee.objects.all()
    summary_data = []

    # User-selected dates
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # If no dates chosen → get current week range (Mon–Sun)
    if not start_date or not end_date:
        today = timezone.now().date()
        start_date = today - timedelta(days=today.weekday())     # Monday
        end_date = start_date + timedelta(days=6)                # Sunday
    else:
        start_date = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = timezone.datetime.strptime(end_date, "%Y-%m-%d").date()

    # Summary calculation
    for emp in employees:
        works = emp.works.filter(date__range=[start_date, end_date])
        advances = emp.advances.filter(date__range=[start_date, end_date])

        total_bricks = sum(w.quantity for w in works)
        total_amount = sum(Decimal(w.calculate_amount()) for w in works)
        total_advance = sum(Decimal(a.amount) for a in advances)
        balance = total_amount - total_advance

        summary_data.append({
            'employee': emp,
            'total_bricks': total_bricks,
            'total_amount': total_amount,
            'total_advance': total_advance,
            'balance': balance,
        })

    return render(request, 'bricks_out/weekly_summary.html', {
        'summary_data': summary_data,
        'start_date': start_date,
        'end_date': end_date,
    })


from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from decimal import Decimal
from datetime import timedelta

from datetime import timedelta, date
from django.db.models import Sum
from decimal import Decimal
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.db.models import Sum
from .models import Employee, BrickOutLoan, BrickOutSaving

def employee_ledger(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    # Fetch related data
    works = employee.works.all().order_by('date')
    advances_list = employee.advances.all().order_by('-date')
    payments_list = employee.payment_set.all().order_by('-date')
    deductions_list = employee.advance_deductions.all().order_by('-date')
    loan_list = BrickOutLoan.objects.filter(employee=employee).order_by('-date')
    saving_list = BrickOutSaving.objects.filter(employee=employee).order_by('-date')

    # WEEK-WISE DATA (Saturday → Friday)
    all_dates = [item.date for item in works] + \
                [item.date for item in advances_list] + \
                [item.date for item in payments_list] + \
                [item.date for item in deductions_list] + \
                [item.date for item in loan_list] + \
                [item.date for item in saving_list]

    start_date = min(all_dates) if all_dates else date.today()
    end_date = max(all_dates) if all_dates else date.today()

    # Generate week ranges
    current = start_date
    week_data_list = []
    week_number = 1
    while current <= end_date:
        weekday = current.weekday()
        days_since_saturday = (weekday - 5) % 7
        week_start = current - timedelta(days=days_since_saturday)
        week_end = week_start + timedelta(days=6)

        # Filter data by week
        week_works = [w for w in works if week_start <= w.date <= week_end]
        week_advances = [a for a in advances_list if week_start <= a.date <= week_end]
        week_payments = [p for p in payments_list if week_start <= p.date <= week_end]
        week_deductions = [d for d in deductions_list if week_start <= d.date <= week_end]
        week_savings = [s for s in saving_list if week_start <= s.date <= week_end]

        # Weekly totals
        week_total_bricks = sum(w.quantity for w in week_works)
        week_total_amount = sum(Decimal(w.calculate_amount()) for w in week_works)
        week_total_advances = sum(a.amount for a in week_advances)
        week_total_deductions = sum(d.amount for d in week_deductions)
        week_total_payments = sum(p.amount for p in week_payments)
        week_total_savings = sum(s.amount for s in week_savings)
        print(week_total_amount)
        print(week_total_advances)
        print(week_total_deductions)
        print(week_total_payments)
        print(week_total_savings)
        # Weekly balance including savings
        week_balance = week_total_amount - week_total_advances  - week_total_payments - week_total_savings

        week_data_list.append({
            "week_number": week_number,
            "week_start": week_start,
            "week_end": week_end,
            "works": week_works,
            "advances": week_advances,
            "payments": week_payments,
            "deductions": week_deductions,
            "savings": week_savings,
            "week_bricks": week_total_bricks,
            "week_total": week_total_amount,
            "week_advances": week_total_advances,
            "week_deductions": week_total_deductions,
            "week_payments": week_total_payments,
            "week_savings": week_total_savings,
            "week_balance": week_balance,
        })

        current += timedelta(days=7)
        week_number += 1

    # Reverse weeks to show latest on top
    week_data_list = list(reversed(week_data_list))
    for idx, week in enumerate(week_data_list, start=1):
        week['week_number'] = idx  # Latest week is week 1

    # PAGINATE WEEKS (1 per page)
    paginator = Paginator(week_data_list, 1)
    week_page_number = request.GET.get('week_page', 1)
    week_data = paginator.get_page(week_page_number)

    # Use current week totals for summary card
    current_week = week_data.object_list[0] if week_data.object_list else {}
    total_bricks = current_week.get('week_bricks', 0)
    total_amount = current_week.get('week_total', 0)
    total_advance = current_week.get('week_advances', 0)
    total_deducted = current_week.get('week_deductions', 0)
    total_paid = current_week.get('week_payments', 0)
    total_saving_week = current_week.get('week_savings', 0)
    balance = current_week.get('week_balance', 0)

    # PAGINATE ADVANCES
    adv_paginator = Paginator(advances_list, 10)
    adv_page_number = request.GET.get('adv_page', 1)
    advances = adv_paginator.get_page(adv_page_number)

    # PAGINATE DEDUCTIONS
    ded_paginator = Paginator(deductions_list, 10)
    ded_page_number = request.GET.get('ded_page', 1)
    deductions = ded_paginator.get_page(ded_page_number)

    # PAGINATE PAYMENTS
    pay_paginator = Paginator(payments_list, 10)
    pay_page_number = request.GET.get('pay_page', 1)
    payments = pay_paginator.get_page(pay_page_number)

    # Loans and savings remain full (no pagination)
    loans = loan_list
    savings = saving_list

    # Total loan and total savings for all weeks (unchanged)
    total_loan = loan_list.aggregate(total=Sum('amount'))['total'] or 0
    total_saving = saving_list.aggregate(total=Sum('amount'))['total'] or 0

    return render(request, "bricks_out/employee_ledger.html", {
        "employee": employee,
        "week_data": week_data,
        "advances": advances,
        "deductions": deductions,
        "payments": payments,
        "loans": loans,
        "savings": savings,
        "total_loan": total_loan,
        "total_saving": total_saving,
        "total_bricks": total_bricks,
        "total_amount": total_amount,
        "total_advance": total_advance,
        "total_deducted": total_deducted,
        "total_paid": total_paid,
        "total_saving_week": total_saving_week,  # weekly saving
        "balance": balance,
    })




from django.shortcuts import render, redirect
from .forms import BrickOutLoanForm, BrickOutSavingForm
def add_loan(request):
    if request.method == "POST":
        form = BrickOutLoanForm(request.POST)
        if form.is_valid():
            loan = form.save()
            return redirect("bricks_out:employee_ledger", pk=loan.employee.id)

    else:
        form = BrickOutLoanForm()

    return render(request, "bricks_out/add_loan.html", {"form": form})


def add_saving(request):
    if request.method == "POST":
        form = BrickOutSavingForm(request.POST)
        if form.is_valid():
            saving=form.save()
            
            return redirect("bricks_out:employee_ledger", pk=saving.employee.id)


    return render(request, "bricks_out/add_saving.html", {
        "form": BrickOutSavingForm()
    })
