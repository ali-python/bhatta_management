from django.urls import path
from . import views

urlpatterns = [
    path("employee/", views.hourly_dashboard, name="employees_dashboard"),
    path("add-advance/", views.add_advance, name="add_advance"),
    path("add-saving/", views.add_saving, name="add_saving"),
    path("pay/<int:emp_id>/", views.give_payment, name="give_payment"),
    path("employee/<int:emp_id>/", views.employee_detail, name="employee_detail"),
    path("add-loan/", views.add_loan, name="add_loan"),

]
