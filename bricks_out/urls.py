from django.urls import path
from . import views

urlpatterns = [

    path('brickrates/', views.BrickRateListView.as_view(), name='brickrate_list'),
    path('brickrates/create/', views.BrickRateCreateView.as_view(), name='brickrate_create'),
    path('brickrates/<int:pk>/edit/', views.BrickRateUpdateView.as_view(), name='brickrate_update'),

    path('brickworks/', views.BrickWorkListView.as_view(), name='brickwork_list'),
    path('brickworks/create/', views.BrickWorkCreateView.as_view(), name='brickwork_create'),
    path('brickworks/<int:pk>/edit/', views.BrickWorkUpdateView.as_view(), name='brickwork_update'),

    path('advances/', views.AdvanceListView.as_view(), name='advance_list'),
    path('advances/create/', views.AdvanceCreateView.as_view(), name='advance_create'),
    path('advances/<int:pk>/edit/', views.AdvanceUpdateView.as_view(), name='advance_update'),

    path('summary/', views.weekly_summary, name='weekly_summary'),

    path('employees/<int:pk>/ledger/', views.employee_ledger, name='employee_ledger'),
    path("add-loan/", views.add_loan, name="add_loan"),
    path("add-saving/", views.add_saving, name="add_saving"),

]
