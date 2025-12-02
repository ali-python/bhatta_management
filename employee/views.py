from django.shortcuts import render
from django.views.generic import ListView, FormView, UpdateView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from .models import Employee
from .forms import EmployeeForm


class AddEmployee(FormView):
    form_class = EmployeeForm
    template_name = 'employee/create_employee.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            AddEmployee, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        print(form.errors)
        form.save()
        return HttpResponseRedirect(reverse('employee:list'))

    def form_invalid(self, form):
        return super(AddEmployee, self).form_invalid(form)


class EmployeeList(ListView):
    model = Employee
    template_name = 'employee/list_employee.html'
    paginate_by = 100
    ordering = '-id'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            EmployeeList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset
        if not queryset:
            queryset = Employee.objects.all().order_by('-id')

        if self.request.GET.get('employee_name'):
            queryset = queryset.filter(
                name__icontains=self.request.GET.get('employee_name'))

        return queryset.order_by('-id')

class UpdateEmployee(UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee/update_employee.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            UpdateEmployee, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse('employee:list'))

    def form_invalid(self, form):
        return super(UpdateEmployee, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(UpdateEmployee, self).get_context_data(**kwargs)
        employee = Employee.objects.all()
        context.update({
            'employee': employee
        })
        return context