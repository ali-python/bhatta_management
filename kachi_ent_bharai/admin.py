from django.contrib import admin
from .models import *

admin.site.register(KachiBrickEmployee)
admin.site.register(KachiBrickWorkEntry)
admin.site.register(KachiBrickAdvance)
admin.site.register(KachiBrickPayment)
admin.site.register(KachiBrickSaving)
admin.site.register(KachiBrickLoan)
admin.site.register(KachiBrickAdvanceDeduction)