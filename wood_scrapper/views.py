from django.shortcuts import render, redirect, get_object_or_404
from .models import WoodScraper, ScrapAdvance, DailyScrapReceive
from django.utils import timezone
from datetime import timedelta

def wood_dashboard(request):
    scrapers = WoodScraper.objects.count()
    total_advances = ScrapAdvance.objects.count()

    total_parcels_advanced = sum(a.total_parcels for a in ScrapAdvance.objects.all())
    total_parcels_received = sum(a.received_parcels for a in ScrapAdvance.objects.all())
    total_parcels_pending = total_parcels_advanced - total_parcels_received

    last_7_days = timezone.now().date() - timedelta(days=7)
    recent_entries = DailyScrapReceive.objects.filter(date__gte=last_7_days).order_by('-date')[:20]

    return render(request, "wood/dashboard.html", {
        "scrapers": scrapers,
        "total_advances": total_advances,
        "total_parcels_advanced": total_parcels_advanced,
        "total_parcels_received": total_parcels_received,
        "total_parcels_pending": total_parcels_pending,
        "recent_entries": recent_entries,
    })

# ---------------------------
# Scraper List + Add
# ---------------------------

def scraper_list(request):
    scrapers = WoodScraper.objects.all()
    return render(request, "wood/scraper_list.html", {"scrapers": scrapers})


def scraper_add(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        WoodScraper.objects.create(name=name, phone=phone, address=address)
        return redirect("wood_scrapper:scraper_list")

    return render(request, "wood/scraper_add.html")


# ---------------------------
# Advance Add
# ---------------------------

def advance_add(request, scraper_id):
    scraper = get_object_or_404(WoodScraper, id=scraper_id)

    if request.method == "POST":
        total_parcels = int(request.POST.get("total_parcels"))
        parcel_rate = int(request.POST.get("parcel_rate", 500))

        ScrapAdvance.objects.create(
            wood_scraper=scraper,
            total_parcels=total_parcels,
            parcel_rate=parcel_rate
        )

        return redirect("wood_scrapper:scraper_list")

    return render(request, "wood/advance_add.html", {"scraper": scraper})


# ---------------------------
# Advance Ledger
# ---------------------------

def advance_ledger(request, advance_id):
    advance = get_object_or_404(ScrapAdvance, id=advance_id)
    daily = advance.daily_entries.order_by("-date")

    return render(request, "wood/advance_ledger.html", {
        "advance": advance,
        "daily": daily,
    })


# ---------------------------
# Daily Parcel Add
# ---------------------------

def daily_add(request, advance_id):
    advance = get_object_or_404(ScrapAdvance, id=advance_id)

    if request.method == "POST":
        parcels = int(request.POST.get("parcels_received"))
        remarks = request.POST.get("remarks")

        # Prevent entering more than pending
        if parcels > advance.pending_parcels:
            parcels = advance.pending_parcels

        DailyScrapReceive.objects.create(
            scrap_advance=advance,
            parcels_received=parcels,
            remarks=remarks
        )

        return redirect("wood_scrapper:advance_ledger", advance_id=advance.id)

    return render(request, "wood/daily_add.html", {"advance": advance})
