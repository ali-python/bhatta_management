from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Payment
from .forms import PaymentForm
from django.db import transaction
from django.db.models import Sum
from decimal import Decimal
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import Payment
from bricks_out.models import AdvanceDeduction
from employee.models import Employee

class PaymentListView(ListView):
    model = Payment
    template_name = 'payment/payment_list.html'
    paginate_by = 10 
    ordering = '-id'

    
def get_outstanding_advance(employee):
    total_advance = employee.advances.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_deducted = employee.advance_deductions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    return total_advance - total_deducted


class PaymentCreateView(CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payment/payment_form.html'
    success_url = reverse_lazy('payment:payment_list')

    def get_initial(self):
        initial = super().get_initial()
        emp_id = self.request.GET.get('employee')

        if emp_id:
            initial['employee'] = emp_id

        return initial

    def form_valid(self, form):
        payment = form.save(commit=False)
        employee = payment.employee

        # Calculate outstanding advance BEFORE saving
        outstanding = get_outstanding_advance(employee)

        with transaction.atomic():
            # Save payment first
            payment.save()

            # Deduct full outstanding advance (not limited by payment amount)
            if outstanding > 0:
                AdvanceDeduction.objects.create(
                    employee=employee,
                    payment=payment,
                    date=payment.date,
                    amount=outstanding,   # 💥 FIXED: deduct full amount
                )

                # Reduce the payment *actual money given*
                # payment.amount = payment.amount - outstanding
                payment.save()

        return super().form_valid(form)








class PaymentUpdateView(UpdateView):
    model = Payment
    fields = ['employee', 'date', 'amount', 'remarks']
    template_name = 'payment/payment_form.html'
    success_url = reverse_lazy('payment:payment_list')
