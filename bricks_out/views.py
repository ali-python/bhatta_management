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

def employee_ledger(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    # MAIN RELATED DATA ------------------------------------------------------
    works = employee.works.all().order_by('date')
    advances_list = employee.advances.all().order_by('-date')
    payments_list = employee.payment_set.all().order_by('-date')
    deductions_list = employee.advance_deductions.all().order_by('-date')

    # NEW: Loan + Saving -----------------------------------------------------
    loan_list = BrickOutLoan.objects.filter(employee=employee).order_by('-date')
    saving_list = BrickOutSaving.objects.filter(employee=employee).order_by('-date')

    # SUMMARY --------------------------------------------------------------
    total_bricks = works.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_amount = sum(Decimal(w.calculate_amount()) for w in works)

    total_advance = advances_list.aggregate(total=Sum('amount'))['total'] or Decimal('0.0')
    total_deducted = deductions_list.aggregate(total=Sum('amount'))['total'] or Decimal('0.0')
    remaining_advance = total_advance - total_deducted

    total_paid = payments_list.aggregate(total=Sum('amount'))['total'] or Decimal('0.0')

    # NEW: totals for loan + saving
    total_loan = loan_list.aggregate(total=Sum('amount'))['total'] or Decimal('0.0')
    total_saving = saving_list.aggregate(total=Sum('amount'))['total'] or Decimal('0.0')

    # BALANCE LOGIC ---------------------------------------------------------
    if total_paid == 0 and total_deducted == 0:
        balance = total_amount - total_advance
    else:
        balance = total_amount - (total_paid + total_deducted) - total_saving

    # WEEK-WISE GROUPING ----------------------------------------------------
    # WEEK-WISE GROUPING (Saturday → Friday) -------------------------------------
    week_data = {}

    for w in works:
        # Shift date by +1 so week starts Saturday instead of Monday
        shifted = w.date + timedelta(days=1)
        year, week, _ = shifted.isocalendar()
        key = f"{year}-W{week}"

        if key not in week_data:
            # Real week start (Saturday)
            start_date = w.date - timedelta(days=(w.date.weekday() + 1) % 7)
            end_date = start_date + timedelta(days=6)

            week_data[key] = {
                "week_number": week,
                "start_date": start_date,
                "end_date": end_date,
                "records": [],
                "week_total": 0,
                "week_bricks": 0,
            }

        week_data[key]["records"].append(w)
        week_data[key]["week_total"] += w.calculate_amount()
        week_data[key]["week_bricks"] += w.quantity

    week_data_list = list(week_data.values())


    # PAGINATION ------------------------------------------------------------
    week_page = Paginator(week_data_list, 10).get_page(request.GET.get('weeks_page'))
    adv_page = Paginator(advances_list, 20).get_page(request.GET.get('adv_page'))
    pay_page = Paginator(payments_list, 20).get_page(request.GET.get('pay_page'))
    ded_page = Paginator(deductions_list, 20).get_page(request.GET.get("ded_page"))

    # NEW: loans + savings pagination
    loan_page = Paginator(loan_list, 20).get_page(request.GET.get("loan_page"))
    saving_page = Paginator(saving_list, 20).get_page(request.GET.get("saving_page"))

    # RENDER ------------------------------------------------------------
    return render(request, "bricks_out/employee_ledger.html", {
        "employee": employee,

        "total_bricks": total_bricks,
        "total_amount": total_amount,

        "total_advance": total_advance,
        "total_deducted": total_deducted,
        "remaining_advance": remaining_advance,

        "total_paid": total_paid,
        "balance": balance,

        # NEW totals
        "total_loan": total_loan,
        "total_saving": total_saving,

        # Paginated data
        "week_data": week_page,
        "advances": adv_page,
        "payments": pay_page,
        "deductions": ded_page,
        "loans": loan_page,
        "savings": saving_page,
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
