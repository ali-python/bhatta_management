from django.db import models

class WoodScraper(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class ScrapAdvance(models.Model):
    wood_scraper = models.ForeignKey(WoodScraper, on_delete=models.CASCADE, related_name="advances")
    total_parcels = models.PositiveIntegerField()
    parcel_rate = models.PositiveIntegerField(default=500)
    date_given = models.DateField(auto_now_add=True)

    @property
    def total_amount(self):
        return self.total_parcels * self.parcel_rate

    @property
    def received_parcels(self):
        return sum(i.parcels_received for i in self.daily_entries.all())

    @property
    def pending_parcels(self):
        return self.total_parcels - self.received_parcels

    def __str__(self):
        return f"Advance #{self.id} - {self.wood_scraper.name}"


class DailyScrapReceive(models.Model):
    scrap_advance = models.ForeignKey(
        ScrapAdvance, on_delete=models.CASCADE, related_name="daily_entries"
    )
    date = models.DateField(auto_now_add=True)
    parcels_received = models.PositiveIntegerField()
    remarks = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.date} - {self.parcels_received} parcels"
