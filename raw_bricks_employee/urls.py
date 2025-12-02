from django.urls import path
from . import views


urlpatterns = [
    path("dashboard/", views.bricks_dashboard, name="dashboard"),
    path("update/", views.update_bricks, name="update_bricks"),

    path("advance/", views.add_brick_advance, name="add_advance"),
    path("saving/", views.add_brick_saving, name="add_saving"),

    path("pay/<int:emp_id>/", views.give_brick_payment, name="give_payment"),

    path("detail/<int:emp_id>/", views.brick_employee_detail, name="employee_detail"),
    path("add-loan/", views.add_loan, name="add_loan"),

]
