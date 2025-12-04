from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('add_worker/', views.add_worker, name='add_worker'),
    path('add_bhatta/', views.add_bhatta, name='add_bhatta'),
    path('add_weekly_report/', views.add_weekly_report, name='add_weekly_report'),
    path('yearly_settlement/', views.yearly_settlement_create, name='yearly_settlement'),
    # path('yearly_settlement/<int:worker_id>/', views.yearly_settlement_create, name='yearly_settlement'),
    path('yearly_settlement/<int:worker_id>/<int:bhatta_id>', views.yearly_settlement_create, name='yearly_settlement'),
    path('yearly_settlement/update/<int:pk>/', views.yearly_settlement_update, name='yearly_settlement_update'),

    path('worker_ledger/', views.worker_ledger, name='worker_ledger'),
    # path('', views.worker_ledger, name='worker_ledger'),        # ledger listing
    path('detail/<int:worker_id>/', views.worker_detail, name='detail'),  # per-worker ledger
    path('add_advance/', views.add_advance, name='add_advance'),
    path('add_advance/<int:worker_id>/', views.add_advance, name='add_advance'),

    path('add_loan/', views.add_loan, name='add_loan'),
    path('add_loan/<int:worker_id>/', views.add_loan, name='add_loan'),

    path('<int:worker_id>/weekly-report/<int:report_id>/delete/', 
     views.weekly_report_delete, 
     name='weekly_report_delete'),



]

