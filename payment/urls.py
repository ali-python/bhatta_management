from django.urls import path
from . import views

urlpatterns = [
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/add/', views.PaymentCreateView.as_view(), name='payment_add'),
    path('payments/<int:pk>/edit/', views.PaymentUpdateView.as_view(), name='payment_update'),
]