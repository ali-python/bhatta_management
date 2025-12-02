from django.contrib import admin
from .models import *

admin.site.register(HourlyEmployee)
admin.site.register(HourEntry)
admin.site.register(HourlyAdvance)
admin.site.register(HourlySaving)
admin.site.register(HourlyPayment)
admin.site.register(HourlyLoan)