from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.shortcuts import redirect
from django.db.models import Q
from decimal import Decimal
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from .models import *
from django.utils import timezone
from django.db.models import Sum
from .forms import *
from product.models import Product,StockOut
# --- TractorEmployee Views ---
class TractorEmployeeListView(ListView):
    model = TractorEmployee
    template_name = 'tractor/tractoremployee_list.html'
    paginate_by = 50

class TractorEmployeeCreateView(CreateView):
    model = TractorEmployee
    fields = ['name', 'phone', 'address', 'role']
    template_name = 'tractor/employee_form.html'
    success_url = reverse_lazy('tractor:dashboard')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        return form

class TractorEmployeeUpdateView(UpdateView):
    model = TractorEmployee
    fields = ['name', 'phone', 'address', 'role']
    template_name = 'tractor/employee_form.html'
    success_url = reverse_lazy('tractor:employee_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        return form


# --- Tractor Views ---
class TractorListView(ListView):
    model = Tractor
    template_name = 'tractor/tractor_list.html'

class TractorCreateView(CreateView):
    model = Tractor
    fields = ['name']
    template_name = 'tractor/tractor_form.html'
    success_url = reverse_lazy('tractor:tractor_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['name'].widget.attrs.update({'class': 'form-control'})
        return form

class TractorUpdateView(UpdateView):
    model = Tractor
    fields = ['name']
    template_name = 'tractor/tractor_form.html'
    success_url = reverse_lazy('tractor:tractor_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['name'].widget.attrs.update({'class': 'form-control'})
        return form


# --- TractorTrip Views ---
class TractorTripListView(ListView):
    model = TractorTrip
    template_name = 'tractor/trip_list.html'
    paginate_by = 50
    ordering = ['-id'] # Order by descending id

from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.utils import timezone
from decimal import Decimal
from .models import TractorTrip, TractorEmployee, Tractor, Customer, CustomerLedger

from decimal import Decimal
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.utils import timezone

class TractorTripCreateView(CreateView):
    model = TractorTrip
    fields = [
        'tractor', 'driver', 'conductor', 'date',
        'bricks_carried', 'brick_type', 'brick_rate', 'trip_amount', 'customer'
    ]
    template_name = 'tractor/trip_form.html'
    success_url = reverse_lazy('tractor:dashboard')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        return form

    @transaction.atomic
    def form_valid(self, form):
        # Handle new customer inline
        new_customer_name = self.request.POST.get('new_customer_name')
        new_customer_phone = self.request.POST.get('new_customer_phone')
        new_customer_address = self.request.POST.get('new_customer_address')

        if not form.cleaned_data.get('customer') and new_customer_name:
            customer = Customer.objects.create(
                name=new_customer_name,
                phone=new_customer_phone,
                address=new_customer_address or ''
            )
            form.instance.customer = customer
        else:
            customer = form.cleaned_data.get('customer')

        # Calculate trip amount
        bricks = form.cleaned_data.get('bricks_carried') or 0
        rate = form.cleaned_data.get('brick_rate') or Decimal('0.0')
        trip_amount = Decimal(bricks) * rate
        form.instance.customer_amount = trip_amount

        amount_due = trip_amount
        total_advance_applied = Decimal('0.0')

        # Apply customer advances BEFORE saving the trip
        if customer and trip_amount > 0:
            advances = CustomerAdvance.objects.filter(
                customer=customer,
                used_amount__lt=models.F('amount')
            ).order_by('date')

            for advance in advances:
                if amount_due <= 0:
                    break
                applied = advance.apply_amount(amount_due)
                if applied > 0:
                    amount_due -= applied
                    total_advance_applied += applied

        # Save the trip
        response = super().form_valid(form)

        # Create customer ledger for the trip
        if customer:
            ledger, created = CustomerLedger.objects.get_or_create(
                customer=customer,
                trip=form.instance,
                defaults={
                    'amount_due': amount_due,
                    'paid': (amount_due == 0),
                    'detail': f"Advance applied: {total_advance_applied}" if total_advance_applied else ''
                }
            )

            # Only create payment if advance was applied
            if total_advance_applied > 0:
                CustomerPayment.objects.create(
                    customer=customer,
                    amount=total_advance_applied,
                    trip=form.instance,
                )

        # Create StockOut entry
        product = Product.objects.filter(category__category=form.instance.brick_type).first()
        if product:
            StockOut.objects.create(
                product=product,
                stock_out_quantity=form.instance.bricks_carried,
                selling_price=form.instance.customer_amount,
            )

        return response





        # Deduct advance automatically
        # if customer and trip_amount > 0:
        #     amount_due = trip_amount
        #     total_advance_applied = Decimal('0.0')

        #     # Apply advance
        #     advances = CustomerAdvance.objects.filter(
        #         customer=customer,
        #         used_amount__lt=models.F('amount')
        #     ).order_by('date')

        #     for advance in advances:
        #         if amount_due <= 0:
        #             break
        #         applied = advance.apply_amount(amount_due)
        #         amount_due -= applied
        #         total_advance_applied += applied

        #     # Create ledger only if it doesn't exist
        #     ledger, created = CustomerLedger.objects.get_or_create(
        #         customer=customer,
        #         trip=form.instance,
        #         defaults={
        #             'amount_due': amount_due,
        #             'paid': (amount_due == 0),
        #             'detail': f"Advance applied: {total_advance_applied}" if total_advance_applied else ''
        #         }
        #     )

        #     # If some advance was applied, create a corresponding CustomerPayment
        #     if total_advance_applied > 0:
        #         CustomerPayment.objects.create(
        #             customer=customer,
        #             amount=total_advance_applied,
        #             trip=form.instance,
        #         )
        # return response



class TractorTripUpdateView(UpdateView):
    model = TractorTrip
    form_class = TractorTripForm
    template_name = 'tractor/trip_form.html'
    success_url = reverse_lazy('tractor:trip_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        return form


# --- TractorAdvance Views ---
class TractorAdvanceListView(ListView):
    model = TractorAdvance
    template_name = 'tractor/advance_list.html'
    paginate_by = 50

class TractorAdvanceCreateView(CreateView):
    model = TractorAdvance
    fields = ['employee', 'date', 'amount']
    template_name = 'tractor/advance_form.html'
    success_url = reverse_lazy('tractor:advance_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        return form

class TractorAdvanceUpdateView(UpdateView):
    model = TractorAdvance
    fields = ['employee', 'date', 'amount']
    template_name = 'tractor/advance_form.html'
    success_url = reverse_lazy('tractor:advance_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        return form


# --- TractorPayment Views ---
class TractorPaymentListView(ListView):
    model = TractorPayment
    template_name = 'tractor/payment_list.html'
    paginate_by = 50

# class TractorPaymentCreateView(CreateView):
#     model = TractorPayment
#     fields = ['employee', 'date', 'amount', 'remarks']
#     template_name = 'tractor/payment_form.html'
#     success_url = reverse_lazy('tractor:payment_list')

#     def get_form(self, form_class=None):
#         form = super().get_form(form_class)
#         for field in form.fields.values():
#             field.widget.attrs.update({'class': 'form-control'})
#         return form

def payment_create(request):
    employee_id = request.GET.get("employee")
    selected_employee = None
    remaining_amount = None
    total_paid = 0
    total_trip_amount = 0
    total_advance = 0

    if employee_id:
        selected_employee = TractorEmployee.objects.filter(id=employee_id).first()

        # Compute totals
        trips = TractorTrip.objects.filter(
            Q(driver=selected_employee) | Q(conductor=selected_employee)
        )

        total_trip_amount = sum(
            t.driver_share() if t.driver == selected_employee else t.conductor_share()
            for t in trips
        )

        total_advance = sum(a.amount for a in TractorAdvance.objects.filter(employee=selected_employee))
        total_paid = sum(p.amount for p in TractorPayment.objects.filter(employee=selected_employee))

        remaining_amount = total_trip_amount - total_advance - total_paid

    if request.method == "POST":
        post_data = request.POST.copy()
        # Make sure employee field is set if selected_employee exists
        if selected_employee:
            post_data["employee"] = selected_employee.id

        form = TractorPaymentForm(post_data)
        if form.is_valid():
            form.save()
            return redirect("tractor:dashboard")
    else:
        initial = {}
        if selected_employee:
            initial["employee"] = selected_employee
        form = TractorPaymentForm(initial=initial)

    return render(request, "tractor/payment_form.html", {
        "form": form,
        "selected_employee": selected_employee,
        "remaining_amount": remaining_amount,
        "total_paid": total_paid,
        "total_trip_amount": total_trip_amount,
        "total_advance": total_advance,
    })


class TractorPaymentUpdateView(UpdateView):
    model = TractorPayment
    fields = ['employee', 'date', 'amount', 'remarks']
    template_name = 'tractor/payment_form.html'
    success_url = reverse_lazy('tractor:payment_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        return form


# --- Ledger / Weekly Summary ---
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from datetime import timedelta
from decimal import Decimal
from collections import defaultdict

def employee_ledger(request, pk):
    employee = get_object_or_404(TractorEmployee, pk=pk)

    all_trips = TractorTrip.objects.filter(
        Q(driver=employee) | Q(conductor=employee)
    ).order_by("-date")

    # GROUP TRIPS SATURDAY → FRIDAY
    week_groups = defaultdict(list)
    for trip in all_trips:
        weekday = trip.date.weekday()  # Monday=0 ... Sunday=6
        days_since_saturday = (weekday - 5) % 7
        week_start = trip.date - timedelta(days=days_since_saturday)
        week_groups[week_start].append(trip)

    weekly_list = sorted(week_groups.items(), reverse=True)

    # 👉 PAGINATION  — THIS IS REQUIRED
    paginator = Paginator(weekly_list, 5)  # 10 weeks per page
    page = request.GET.get("page")
    weekly_trips = paginator.get_page(page)

    # --- totals ---
    advances = TractorAdvance.objects.filter(employee=employee)
    payments = TractorPayment.objects.filter(employee=employee)
    loan = TractorLoan.objects.filter(employee=employee)
    saving = TractortSaving.objects.filter(employee=employee)
    total_trip_amount = Decimal("0")
    for trip in all_trips:
        if trip.driver == employee:
            total_trip_amount += Decimal(trip.driver_share())
        else:
            total_trip_amount += Decimal(trip.conductor_share())

    total_advance = sum(Decimal(a.amount) for a in advances)
    total_paid = sum(Decimal(p.amount) for p in payments)
    total_loan = sum(Decimal(l.amount) for l in loan)
    total_saving = sum(Decimal(s.amount) for s in saving)
    balance = total_trip_amount - total_advance - total_paid - total_saving

    context = {
        "employee": employee,
        "weekly_trips": weekly_trips,  # IMPORTANT
        "advances": advances,
        "payments": payments,
        "total_trip_amount": total_trip_amount,
        "total_advance": total_advance,
        "total_paid": total_paid,
        "balance": balance,
        "total_loan" : total_loan,
        "total_saving" : total_saving
    }

    return render(request, "tractor/employee_ledger.html", context)

from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from datetime import date, timedelta

def get_week_dates(year, week):
    # First Saturday of the year
    first_day = date(year, 1, 1)
    first_saturday = first_day + timedelta(days=(5 - first_day.weekday()) % 7)
    
    # Week start = Saturday
    week_start = first_saturday + timedelta(weeks=week - 1)
    week_end = week_start + timedelta(days=6)  # Friday
    
    return week_start, week_end


def weekly_summary(request):
    employees = TractorEmployee.objects.all()
    summary_data = []
    now = timezone.now()

    # --- Selected Week/Year ---
    selected_week = request.GET.get("week")
    selected_year = request.GET.get("year")

    if selected_week and selected_year:
        selected_week = int(selected_week)
        selected_year = int(selected_year)
    else:
        selected_year = now.year

        # auto detect the correct custom week
        today = now.date()
        first_saturday = date(selected_year, 1, 1) + timedelta(days=(5 - date(selected_year, 1, 1).weekday()) % 7)
        selected_week = ((today - first_saturday).days // 7) + 1

    # Week start & end for filters
    week_start, week_end = get_week_dates(selected_year, selected_week)

    # --- Build week dropdown list (with dates) ---
    weeks_with_dates = []
    for w in range(1, 54):
        try:
            s, e = get_week_dates(selected_year, w)
            weeks_with_dates.append({"week": w, "start": s, "end": e})
        except:
            pass

    # --- Employee Summary ---
    for emp in employees:

        trips = TractorTrip.objects.filter(
            date__range=(week_start, week_end)
        ).filter(
            Q(driver=emp) | Q(conductor=emp)
        )

        advances = TractorAdvance.objects.filter(
            employee=emp,
            date__range=(week_start, week_end)
        )

        payments = TractorPayment.objects.filter(
            employee=emp,
            date__range=(week_start, week_end)
        )

        total_trip_amount = sum([
            Decimal(t.driver_share()) if t.driver == emp else Decimal(t.conductor_share())
            for t in trips
        ])

        total_advance = sum(Decimal(a.amount) for a in advances)
        total_paid = sum(Decimal(p.amount) for p in payments)

        balance = total_trip_amount - total_advance - total_paid

        summary_data.append({
            "employee": emp,
            "total_trip_amount": total_trip_amount,
            "total_advance": total_advance,
            "total_paid": total_paid,
            "balance": balance,
            "trips": trips,
        })

    # --- PAGINATION ---
    paginator = Paginator(summary_data, 5)  # Show 5 employees per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "selected_week": selected_week,
        "selected_year": selected_year,
        "weeks": weeks_with_dates,
        "years": range(now.year - 5, now.year + 1)
    }

    return render(request, "tractor/weekly_summery.html", context)

from django.shortcuts import render
from django.db.models import Sum

def customer_dashboard(request):
    customers = Customer.objects.all()
    customer_data = []

    for cust in customers:
        trips = TractorTrip.objects.filter(customer=cust)
        payments = TractorPayment.objects.filter(customer=cust)
        total_trip_amount = sum(t.trip_amount for t in trips)
        total_paid = sum(p.amount for p in payments)
        balance = total_trip_amount - total_paid

        customer_data.append({
            "customer": cust,
            "trips_count": trips.count(),
            "total_trip_amount": total_trip_amount,
            "total_paid": total_paid,
            "balance": balance,
        })

    return render(request, "customer/dashboard.html", {
        "customer_data": customer_data
    })

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect



from collections import defaultdict
from django.db.models import Q

from django.core.paginator import Paginator

from django.core.paginator import Paginator
from django.db.models import Sum, Q
from datetime import timedelta
from django.utils import timezone

def tractor_dashboard(request):
    # -------------------------
    # Week Selection
    # -------------------------
    week_offset = int(request.GET.get("week", 0))
    selected_customer_id = request.GET.get("customer")

    today = timezone.now().date() + timedelta(days=week_offset * 7)
    weekday = today.weekday()
    days_since_sat = (weekday - 5) % 7
    week_start = today - timedelta(days=days_since_sat)
    week_end = week_start + timedelta(days=6)

    # -------------------------
    # Fetch Employees & Customers
    # -------------------------
    employees = TractorEmployee.objects.all()
    customers = Customer.objects.all()
    selected_customer = Customer.objects.filter(id=selected_customer_id).first() if selected_customer_id else None

    # -------------------------
    # Employee Table (Lifetime Totals)
    # -------------------------
    employee_rows = []
    for emp in employees:
        trips = TractorTrip.objects.filter(Q(driver=emp) | Q(conductor=emp))
        total_trip_amount = sum(
            Decimal(t.driver_share() if t.driver == emp else t.conductor_share() or 0)
            for t in trips
        )
        total_advance = TractorAdvance.objects.filter(employee=emp).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        total_paid = TractorPayment.objects.filter(employee=emp).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        total_saving = TractortSaving.objects.filter(employee=emp).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        remaining = total_trip_amount - total_advance - total_paid -total_saving
        
        employee_rows.append({
            "employee": emp,
            "total_trip_amount": total_trip_amount,
            "advance": total_advance,
            "paid": total_paid,
            "remaining": remaining,
        })

    employee_paginator = Paginator(employee_rows, 10)
    employee_page_obj = employee_paginator.get_page(request.GET.get("emp_page"))

    # -------------------------
    # Customer Table (Lifetime Totals)
    # -------------------------
    customer_rows = []
    for cust in customers:
        if selected_customer and cust.id != selected_customer.id:
            continue

        # Total trip amount
        total_trip_amount = TractorTrip.objects.filter(customer=cust).aggregate(
            total=Sum('customer_amount')
        )['total'] or Decimal('0')
        total_trip_amount = Decimal(total_trip_amount)

        # Total paid
        total_paid = CustomerPayment.objects.filter(customer=cust).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        total_paid = Decimal(total_paid)

        # Total and remaining advance
        total_advance = CustomerAdvance.objects.filter(customer=cust).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        remaining_advance = CustomerAdvance.objects.filter(customer=cust).aggregate(
            total=Sum(F('amount') - F('used_amount'))
        )['total'] or Decimal('0')

        # Balance = trips total minus payments minus applied advances
        balance = max(total_trip_amount - total_paid - remaining_advance, Decimal('0'))
        print(balance)
        customer_rows.append({
            "customer": cust,
            "total_trip_amount": total_trip_amount,
            "total_paid": total_paid,
            "balance": balance,
        })

    customer_paginator = Paginator(customer_rows, 10)
    customer_page_obj = customer_paginator.get_page(request.GET.get("cust_page"))

    # -------------------------
    # Render
    # -------------------------
    return render(request, "tractor/tractor_dashboard.html", {
        "week_dates": [week_start + timedelta(days=i) for i in range(7)],
        "prev_week": week_offset - 1,
        "next_week": week_offset + 1,
        "employee_page_obj": employee_page_obj,
        "customer_page_obj": customer_page_obj,
        "customers": customers,
        "selected_customer": selected_customer,
    })




def employee_ledger_new(request, pk=None, customer_id=None):
    if pk:
        entity = get_object_or_404(TractorEmployee, pk=pk)
        trips = TractorTrip.objects.filter(Q(driver=entity) | Q(conductor=entity)).order_by("-date")
        advances = TractorAdvance.objects.filter(employee=entity)
        payments = TractorPayment.objects.filter(employee=entity)
    elif customer_id:
        entity = get_object_or_404(Customer, pk=customer_id)
        trips = TractorTrip.objects.filter(customer=entity).order_by("-date")
        advances = []
        payments = TractorPayment.objects.filter(customer=entity)
    
    total_trip_amount = sum([t.driver_share() if hasattr(entity, 'driven_trips') else t.trip_amount for t in trips])
    total_advance = sum(a.amount for a in advances)
    total_paid = sum(p.amount for p in payments)
    balance = total_trip_amount - total_advance - total_paid

    return render(request, "tractor/ledger_detail.html", {
        "entity": entity,
        "trips": trips,
        "advances": advances,
        "payments": payments,
        "balance": balance
    })

from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Customer, TractorTrip, TractorPayment
from .forms import CustomerForm


# -----------------------
# Customer CRUD
# -----------------------

class CustomerListView(ListView):
    model = Customer
    template_name = "tractor/customer_list.html"
    context_object_name = "customers"

    def get_queryset(self):
        q = self.request.GET.get("q")
        qs = Customer.objects.all().order_by("-id")
        if q:
            qs = qs.filter(name__icontains=q)
        return qs


class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "tractor/create_customer.html"
    success_url = reverse_lazy("tractor:customer_list")


class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "tractor/customers_update.html"
    success_url = reverse_lazy("tractor:customer_list")


class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = "tractor/customers_delete.html"
    success_url = reverse_lazy("tractor:customer_list")



from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from .models import Customer, TractorTrip, CustomerPayment, CustomerLedger
from .forms import CustomerPaymentForm

from django.core.paginator import Paginator

from django.db.models import Sum, F, ExpressionWrapper, DecimalField

from decimal import Decimal
from django.db.models import Sum

def customer_ledger(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)

    trips_list = TractorTrip.objects.filter(customer=customer).order_by("-date")
    payments_list = CustomerPayment.objects.filter(customer=customer).order_by("-date")
    advances_list = CustomerAdvance.objects.filter(customer=customer).order_by("-date")
    ledger_list = CustomerLedger.objects.filter(customer=customer).order_by("-date")

    # Pagination
    trip_page = request.GET.get('trip_page', 1)
    payment_page = request.GET.get('payment_page', 1)
    ledger_page = request.GET.get('ledger_page', 1)
    advance_page = request.GET.get('advance_page', 1)

    trips = Paginator(trips_list, 10).get_page(trip_page)
    payments = Paginator(payments_list, 10).get_page(payment_page)
    ledger_items = Paginator(ledger_list, 10).get_page(ledger_page)
    advances = Paginator(advances_list, 10).get_page(advance_page)

    # Handle new payment
    if request.method == "POST":
        amount = request.POST.get("amount")
        if amount:
            amount = Decimal(amount)
            CustomerPayment.objects.create(customer=customer, amount=amount)
            return redirect("tractor:customer_ledger", customer_id=customer.id)

    # Totals
    total_trip_amount = trips_list.aggregate(total=Sum('customer_amount'))['total'] or Decimal('0')
    total_paid = payments_list.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_advance = advances_list.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    remaining_advance = advances_list.aggregate(
        total=Sum(F('amount') - F('used_amount'))
    )['total'] or Decimal('0')

    # Balance = trips total minus payments minus applied advances
    balance = max(total_trip_amount - total_paid  - remaining_advance, Decimal('0'))

    return render(request, "tractor/customer_ledger.html", {
        "customer": customer,
        "trips": trips,
        "payments": payments,
        "ledger_items": ledger_items,
        "advances": advances,
        "total_trip_amount": total_trip_amount,
        "total_paid": total_paid,
        "total_advance": total_advance,
        "remaining_advance": remaining_advance,
        "balance": balance,
    })




class InvoiceDetailTemplateView(TemplateView):
    template_name = 'tractor/invoice.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            InvoiceDetailTemplateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(InvoiceDetailTemplateView, self).get_context_data(**kwargs)
        invoice = TractorTrip.objects.get(id=self.kwargs.get('pk'))
        context.update({
            'invoice': invoice
        })
        return context

def customer_ledger_create(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)

    if request.method == "POST":
        form = CustomerLedgerForm(request.POST)
        if form.is_valid():
            ledger = form.save(commit=False)
            ledger.customer = customer
            ledger.save()
            return redirect("tractor:customer_ledger", customer.id)
    else:
        form = CustomerLedgerForm()

    return render(request, "tractor/create_customer_ledger.html", {
        "form": form,
        "customer": customer
    })

def create_customer_advance(request, customer_pk=None):
    customer = None
    if customer_pk:
        customer = Customer.objects.filter(pk=customer_pk).first()
        if not customer:
            return redirect('tractor:customer_list')  # or 404

    if request.method == 'POST':
        form = CustomerAdvanceForm(request.POST)
        if form.is_valid():
            advance = form.save(commit=False)
            if customer:
                advance.customer = customer
            advance.save()
            return redirect('tractor:customer_ledger', customer_pk)
        else:
            print(form.errors)
    else:
        form = CustomerAdvanceForm()

    return render(request, 'tractor/customer_advance_payment.html', {'form': form, 'customer': customer})


def add_loan(request):
    if request.method == "POST":
        form = TractorLoanForm(request.POST)
        if form.is_valid():
            loan = form.save()
            return redirect("tractor:employee_ledger", pk=loan.employee.id)

    else:
        form = TractorLoanForm()

    return render(request, "tractor/add_loan.html", {"form": form})


def add_saving(request):
    if request.method == "POST":
        form = TractorSavingForm(request.POST)
        if form.is_valid():
            saving=form.save()
            
            return redirect("tractor:employee_ledger", pk=saving.employee.id)


    return render(request, "tractor/add_saving.html", {
        "form": TractorSavingForm()
    })
