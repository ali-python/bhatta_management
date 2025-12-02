from django.urls import path
from .views import *

urlpatterns = [
    path('add', AddEmployee.as_view(), name='add'),
    path('list', EmployeeList.as_view(), name='list'),
    path('update/<int:pk>/', UpdateEmployee.as_view(), name='update'),

]