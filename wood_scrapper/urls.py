from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.wood_dashboard, name="wood_dashboard"),

    path("scrapers/", views.scraper_list, name="scraper_list"),
    path("scrapers/add/", views.scraper_add, name="scraper_add"),

    path("advance/<int:scraper_id>/add/", views.advance_add, name="advance_add"),
    path("advance/<int:advance_id>/ledger/", views.advance_ledger, name="advance_ledger"),

    path("daily/<int:advance_id>/add/", views.daily_add, name="daily_add"),
]
