from django.contrib import admin
from .models import Bhatta, Worker, WeeklyReport, Advance, Loan, YearlySettlement, LoanDeduction, AdvanceDeduction

admin.site.register(Bhatta)
admin.site.register(Worker)
admin.site.register(WeeklyReport)
admin.site.register(Advance)
admin.site.register(Loan)
admin.site.register(YearlySettlement)
admin.site.register(LoanDeduction)
admin.site.register(AdvanceDeduction)   