from django.shortcuts import render
from expense.forms import ExpenseFormView
from expense.models import Expense
from django.views.generic import ListView, FormView, DeleteView, UpdateView
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone


class AddExpense(FormView):
    form_class = ExpenseFormView
    template_name = 'expense/add_expense.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            AddExpense, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse('expense:list'))

    def form_invalid(self, form):
        return super(AddExpense, self).form_invalid(form)


from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta


class ExpenseList(ListView):
    template_name = 'expense/expense_list.html'
    model = Expense
    paginate_by = 100
    ordering = '-id'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('common:login'))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Expense.objects.all().order_by('-id')

        if self.request.GET.get('date'):
            queryset = queryset.filter(
                date__icontains=self.request.GET.get('date')
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Week start (Saturday)
        today = timezone.now().date()
        weekday = today.weekday()  # Mon=0 … Sun=6
        days_since_saturday = (weekday - 5) % 7
        week_start = today - timedelta(days=days_since_saturday)
        week_end = week_start + timedelta(days=6)

        # Weekly sum
        weekly_total = Expense.objects.filter(
            date__range=[week_start, week_end]
        ).aggregate(total=Sum('amount'))['total'] or 0

        context['week_start'] = week_start
        context['week_end'] = week_end
        context['weekly_total'] = weekly_total

        return context


    # def get_context_data(self, **kwargs):
    #     context = super(ExpenseList, self).get_context_data(**kwargs)
    #     expense = (
    #         Expense.objects.all()
    #     )
    #     context.update({
    #         'expense': expense
    #     })
    #     return context


class UpdateExpense(UpdateView):
    model = Expense
    form_class = ExpenseFormView
    template_name = 'expense/update_expense.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            UpdateExpense, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse('expense:list'))

    def form_invalid(self, form):
        return super(UpdateExpense, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(UpdateExpense, self).get_context_data(**kwargs)
        expense = Expense.objects.all()
        context.update({
            'expense': expense
        })
        return context


class DeleteExpense(DeleteView):
    model = Expense
    success_url = reverse_lazy('expense:list')
    success_message = ''

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            DeleteExpense, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
