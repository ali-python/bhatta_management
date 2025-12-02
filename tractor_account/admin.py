from django.contrib import admin
from .models import *


admin.site.register(Tractor)
admin.site.register(TractorPayment)
admin.site.register(TractorAdvance)
admin.site.register(TractorEmployee)
admin.site.register(TractorTrip)
admin.site.register(Customer)
admin.site.register(CustomerLedger)
admin.site.register(CustomerPayment)
admin.site.register(CustomerAdvance)
