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

    # Collect all dates
    all_dates = (
        list(works.values_list('date', flat=True)) +
        list(advances_list.values_list('date', flat=True)) +
        list(payments_list.values_list('date', flat=True)) +
        list(deductions_list.values_list('date', flat=True)) +
        list(loan_list.values_list('date', flat=True)) +
        list(saving_list.values_list('date', flat=True))
    )

    if not all_dates:
        start_date = end_date = date.today()
    else:
        start_date = min(all_dates)
        end_date = max(all_dates)

    # 🔥 FIX: force start from Saturday
    start_weekday = start_date.weekday()
    days_since_saturday = (start_weekday - 5) % 7
    current = start_date - timedelta(days=days_since_saturday)

    week_data_list = []
    week_number = 1

    while current <= end_date:
        week_start = current
        week_end = week_start + timedelta(days=6)

        # ORM filtering (accurate + fast)
        week_works = works.filter(date__range=(week_start, week_end))
        week_advances = advances_list.filter(date__range=(week_start, week_end))
        week_payments = payments_list.filter(date__range=(week_start, week_end))
        week_deductions = deductions_list.filter(date__range=(week_start, week_end))
        week_savings = saving_list.filter(date__range=(week_start, week_end))

        # Weekly totals
        week_total_bricks = sum(w.quantity for w in week_works)
        week_total_amount = sum(Decimal(w.calculate_amount()) for w in week_works)
        week_total_advances = week_advances.aggregate(total=Sum('amount'))['total'] or 0
        week_total_deductions = week_deductions.aggregate(total=Sum('amount'))['total'] or 0
        week_total_payments = week_payments.aggregate(total=Sum('amount'))['total'] or 0
        week_total_savings = week_savings.aggregate(total=Sum('amount'))['total'] or 0

        # Weekly balance
        week_balance = (
            week_total_amount
            - week_total_advances
            - week_total_payments
            - week_total_savings
        )

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

    # Latest week first
    week_data_list.reverse()
    for idx, week in enumerate(week_data_list, start=1):
        week['week_number'] = idx

    # Paginate weeks (1 per page)
    paginator = Paginator(week_data_list, 1)
    week_page_number = request.GET.get('week_page', 1)
    week_data = paginator.get_page(week_page_number)

    current_week = week_data.object_list[0] if week_data.object_list else {}

    # Summary card
    total_bricks = current_week.get('week_bricks', 0)
    total_amount = current_week.get('week_total', 0)
    total_advance = current_week.get('week_advances', 0)
    total_deducted = current_week.get('week_deductions', 0)
    total_paid = current_week.get('week_payments', 0)
    total_saving_week = current_week.get('week_savings', 0)
    balance = current_week.get('week_balance', 0)

    # Pagination for other lists
    advances = Paginator(advances_list, 10).get_page(request.GET.get('adv_page', 1))
    deductions = Paginator(deductions_list, 10).get_page(request.GET.get('ded_page', 1))
    payments = Paginator(payments_list, 10).get_page(request.GET.get('pay_page', 1))

    # Totals
    total_loan = loan_list.aggregate(total=Sum('amount'))['total'] or 0
    total_saving = saving_list.aggregate(total=Sum('amount'))['total'] or 0

    return render(request, "bricks_out/employee_ledger.html", {
        "employee": employee,
        "week_data": week_data,
        "advances": advances,
        "deductions": deductions,
        "payments": payments,
        "loans": loan_list,
        "savings": saving_list,
        "total_loan": total_loan,
        "total_saving": total_saving,
        "total_bricks": total_bricks,
        "total_amount": total_amount,
        "total_advance": total_advance,
        "total_deducted": total_deducted,
        "total_paid": total_paid,
        "total_saving_week": total_saving_week,
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
