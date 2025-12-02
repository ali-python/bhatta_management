# tractor/urls.py
from django.urls import path
from . import views

app_name = "tractor"

urlpatterns = [
    # Tractor Employee CRUD
    path('employees/', views.TractorEmployeeListView.as_view(), name='employee_list'),
    path('employees/add/', views.TractorEmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/update/', views.TractorEmployeeUpdateView.as_view(), name='employee_update'),
    path('employees/<int:pk>/ledger/', views.employee_ledger, name='employee_ledger'),

    # Tractor CRUD
    path('tractors/', views.TractorListView.as_view(), name='tractor_list'),
    path('tractors/add/', views.TractorCreateView.as_view(), name='tractor_create'),
    path('tractors/<int:pk>/update/', views.TractorUpdateView.as_view(), name='tractor_update'),

    # Tractor Trip CRUD
    path('trips/', views.TractorTripListView.as_view(), name='trip_list'),
    path('trips/add/', views.TractorTripCreateView.as_view(), name='trip_create'),
    path('trips/<int:pk>/update/', views.TractorTripUpdateView.as_view(), name='trip_update'),

    # Advance Payment for Employees
    path('advance/', views.TractorAdvanceListView.as_view(), name='advance_list'),
    path('advance/add/', views.TractorAdvanceCreateView.as_view(), name='advance_create'),
    path('advance/<int:pk>/update/', views.TractorAdvanceUpdateView.as_view(), name='advance_update'),

    path('payments/', views.TractorPaymentListView.as_view(), name='payment_list'),
    path('payments/add/', views.payment_create, name='payment_create'),
    path('payments/<int:pk>/update/', views.TractorPaymentUpdateView.as_view(), name='payment_update'),
    # Weekly summary
    path('weekly-summary/', views.weekly_summary, name='weekly_summary'),

    #dashboard

    path('dashboard/', views.tractor_dashboard, name='dashboard'),
    # Ledger for employee
    path('ledger/employee/<int:pk>/', views.employee_ledger, name='employee_ledger'),

    # Customer CRUD
    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    path('customers/add/', views.CustomerCreateView.as_view(), name='customer_create'),
    path('customers/<int:pk>/update/', views.CustomerUpdateView.as_view(), name='customer_update'),
    path('customers/<int:pk>/delete/', views.CustomerDeleteView.as_view(), name='customer_delete'),

    # Customer Ledger
    path("customer/<int:customer_id>/ledger/create/", views.customer_ledger_create, name="create_customer_ledger"),
    path('customers/<int:customer_id>/ledger/', views.customer_ledger, name='customer_ledger'),
    path("invoice/<int:pk>/detail", views.InvoiceDetailTemplateView.as_view(), name='invoice_detail'),
    path('customer/<int:customer_pk>/advance/', views.create_customer_advance, name='create_customer_advance'),
    path("add-loan/", views.add_loan, name="add_loan"),
    path("add-saving/", views.add_saving, name="add_saving"),
    ]
