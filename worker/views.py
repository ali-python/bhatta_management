from django.shortcuts import render, redirect, get_object_or_404
from .models import Bhatta, Worker, WeeklyReport, Advance, Loan, YearlySettlement, LoanDeduction, AdvanceDeduction
from django.utils import timezone
from django.db.models import Sum
from datetime import date

def home(request):
    bhattas = Bhatta.objects.all()
    workers = Worker.objects.all()
    return render(request, 'worker/home.html', {'bhattas': bhattas, 'workers': workers})


def add_worker(request):
    if request.method == 'POST':
        name = request.POST['name']
        phone = request.POST['phone']
        bhatta_ids = request.POST.getlist('bhattas')
        worker = Worker.objects.create(name=name, phone=phone)
        worker.bhattas.set(bhatta_ids)
        return redirect('worker:home')
    bhattas = Bhatta.objects.all()
    return render(request, 'worker/add_worker.html', {'bhattas': bhattas})


def add_bhatta(request):
    if request.method == 'POST':
        name = request.POST['name']
        Bhatta.objects.create(name=name)
        return redirect('worker:home')
    return render(request, 'worker/add_bhata.html')


def add_weekly_report(request):
    if request.method == 'POST':
        worker_id = request.POST['worker']
        bhatta_id = request.POST['bhatta']
        week_start = request.POST['week_start']
        week_end = request.POST['week_end']
        bricks = int(request.POST['bricks'])
        WeeklyReport.objects.create(
            worker_id=worker_id,
            bhatta_id=bhatta_id,
            week_start=week_start,
            week_end=week_end,
            bricks_worked=bricks
        )
        return redirect('worker:home')
    workers = Worker.objects.all()
    bhattas = Bhatta.objects.all()
    return render(request, 'worker/add_weekly_report.html', {'workers': workers, 'bhattas': bhattas})


from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from datetime import datetime
from .models import Worker, Bhatta, WeeklyReport, Advance, Loan, YearlySettlement
from django.utils import timezone
from decimal import Decimal
AdvanceDeduction, LoanDeduction

def yearly_settlement_create(request, worker_id=None, bhatta_id=None):
    bhattas = Bhatta.objects.all()
    selected_worker = None
    selected_bhatta = None
    year = timezone.now().year

    total_bricks = 0
    total_advance = 0
    total_loan = 0

    if worker_id and bhatta_id:
        selected_worker = get_object_or_404(Worker, id=worker_id)
        selected_bhatta = get_object_or_404(Bhatta, id=bhatta_id)

        # Total bricks for this worker & bhatta for the year
        total_bricks = WeeklyReport.objects.filter(
            worker=selected_worker,
            bhatta=selected_bhatta,
            week_start__year=year
        ).aggregate(sum=Sum('bricks_worked'))['sum'] or 0

        # Remaining advances for this worker (subtract previous deductions)
        total_advance_paid = AdvanceDeduction.objects.filter(
            advance__worker=selected_worker
        ).aggregate(sum=Sum('deducted_amount'))['sum'] or Decimal('0')

        total_advance_all = Advance.objects.filter(worker=selected_worker).aggregate(sum=Sum('amount'))['sum'] or Decimal('0')
        total_advance = total_advance_all - total_advance_paid

        # Remaining loans for this worker
        total_loan_paid = LoanDeduction.objects.filter(
            loan__worker=selected_worker
        ).aggregate(sum=Sum('deducted_amount'))['sum'] or Decimal('0')

        total_loan_all = Loan.objects.filter(worker=selected_worker).aggregate(sum=Sum('amount'))['sum'] or Decimal('0')
        total_loan = total_loan_all - total_loan_paid

    if request.method == 'POST':
        worker_id = request.POST.get('worker')
        bhatta_id = request.POST.get('bhatta')
        year = int(request.POST.get('year'))
        brick_rate = float(request.POST.get('brick_rate'))

        worker = get_object_or_404(Worker, id=worker_id)
        bhatta = get_object_or_404(Bhatta, id=bhatta_id)

        # Total bricks for selected bhatta and worker
        total_bricks = WeeklyReport.objects.filter(
            worker=worker,
            bhatta=bhatta,
            week_start__year=year
        ).aggregate(sum=Sum('bricks_worked'))['sum'] or 0

        # Remaining advances
        total_advance_paid = AdvanceDeduction.objects.filter(
            advance__worker=worker
        ).aggregate(sum=Sum('deducted_amount'))['sum'] or Decimal('0')

        total_advance_all = Advance.objects.filter(worker=worker).aggregate(sum=Sum('amount'))['sum'] or Decimal('0')
        total_advance = total_advance_all - total_advance_paid

        # Remaining loans
        total_loan_paid = LoanDeduction.objects.filter(
            loan__worker=worker
        ).aggregate(sum=Sum('deducted_amount'))['sum'] or Decimal('0')

        total_loan_all = Loan.objects.filter(worker=worker).aggregate(sum=Sum('amount'))['sum'] or Decimal('0')
        total_loan = total_loan_all - total_loan_paid

        total_earned = Decimal(total_bricks) / Decimal('1000') * Decimal(str(brick_rate))
        amount_to_pay = total_earned - total_advance - total_loan

        payment_made = float(request.POST.get('payment_made', 0))

        # Create the yearly settlement
        settlement = YearlySettlement.objects.create(
            worker=worker,
            bhatta=bhatta,
            year=year,
            total_bricks=total_bricks,
            brick_rate_per_1000=brick_rate,
            total_earned=total_earned,
            total_advance=total_advance,
            total_loan_deducted=total_loan,
            amount_to_pay=amount_to_pay,
            payment_made=payment_made,
        )

        # If negative amount_to_pay, record extra as new advance
        if amount_to_pay < 0:
            Advance.objects.create(
                worker=worker,
                amount=abs(amount_to_pay),
                date=timezone.now()
            )
            amount_to_pay = 0

        # Apply advances deduction
        remaining_deduction = Decimal(total_advance)
        advances = Advance.objects.filter(worker=worker).order_by('date')
        for adv in advances:
            if remaining_deduction <= 0:
                break
            available = adv.amount - (adv.deductions.aggregate(total=Sum('deducted_amount'))['total'] or 0)
            if available <= 0:
                continue
            deduction = min(available, remaining_deduction)
            AdvanceDeduction.objects.create(
                advance=adv,
                settlement=settlement,
                deducted_amount=deduction
            )
            remaining_deduction -= deduction

        # Apply loans deduction
        remaining_loan_deduction = Decimal(total_loan)
        loans = Loan.objects.filter(worker=worker).order_by('date')
        for loan in loans:
            if remaining_loan_deduction <= 0:
                break
            available = loan.amount - (loan.deductions.aggregate(total=Sum('deducted_amount'))['total'] or 0)
            if available <= 0:
                continue
            deduction = min(available, remaining_loan_deduction)
            LoanDeduction.objects.create(
                loan=loan,
                settlement=settlement,
                deducted_amount=deduction
            )
            remaining_loan_deduction -= deduction

        return redirect('worker:detail', worker.id)

    context = {
        'workers': Worker.objects.all(),
        'bhattas': bhattas,
        'selected_worker': selected_worker,
        'selected_bhatta': selected_bhatta,
        'year': year,
        'total_bricks': total_bricks,
        'total_advance': total_advance,
        'total_loan': total_loan,
        'total_earned': 0,
        'amount_to_pay': 0,
        'brick_rate': 0,
        'payment_made': 0,
        'object': None,
    }

    return render(request, 'worker/yearly_form.html', context)

def yearly_settlement_update(request, pk):
    obj = get_object_or_404(YearlySettlement, id=pk)
    workers = Worker.objects.all()
    bhattas = Bhatta.objects.all()

    if request.method == "POST":
        obj.worker_id = request.POST["worker"]
        obj.bhatta_id = request.POST["bhatta"]
        obj.year = int(request.POST["year"])
        obj.brick_rate_per_1000 = float(request.POST["brick_rate"])
        obj.total_advance = float(request.POST.get("total_advance") or 0)
        obj.total_loan_deducted = float(request.POST.get("total_loan_deducted") or 0)
        obj.payment_made = float(request.POST.get("payment_made") or 0)

        # Recalculate total bricks
        obj.total_bricks = WeeklyReport.objects.filter(
            worker=obj.worker, bhatta=obj.bhatta, week_start__year=obj.year
        ).aggregate(Sum("bricks_worked"))["bricks_worked__sum"] or 0

        obj.total_earned = (obj.total_bricks / 1000) * obj.brick_rate_per_1000
        obj.amount_to_pay = obj.total_earned - obj.total_advance - obj.total_loan_deducted

        obj.save()
        return redirect('worker:worker_ledger')

    return render(request, "worker/yearly_form.html", {
        "object": obj,
        "workers": workers,
        "bhattas": bhattas
    })



from django.db.models import Sum

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Worker, Bhatta, WeeklyReport, Advance, Loan, YearlySettlement
from django.utils import timezone
from datetime import date

# ---------- Worker ledger list (yearly settlements / fallback) ----------
def worker_ledger(request):
    """
    Shows a list of YearlySettlement entries. If none exist, shows workers with links.
    """
    settlements = YearlySettlement.objects.select_related('worker', 'bhatta').order_by('worker__name', '-year')

    # If no settlement records, show workers so owner can navigate to worker ledger
    if not settlements.exists():
        workers = Worker.objects.prefetch_related('bhattas').all()
        return render(request, 'worker/worker_ledger.html', {'settlements': [], 'workers': workers})

    return render(request, 'worker/worker_ledger.html', {'settlements': settlements, 'workers': None})


# ---------- Per-worker ledger detail ----------

from django.core.paginator import Paginator
from datetime import datetime, timedelta

from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import get_object_or_404, render
from .models import Worker, WeeklyReport, Advance, Loan, YearlySettlement

from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import get_object_or_404, render
from .models import Worker, WeeklyReport, Advance, Loan, YearlySettlement

def week_starting(date):
    """Return Saturday of the week for a given date."""
    offset = (date.weekday() - 5) % 7
    return date - timedelta(days=offset)

from django.db.models import Sum

def worker_detail(request, worker_id):
    worker = get_object_or_404(Worker.objects.prefetch_related('bhattas'), pk=worker_id)

    week_query = request.GET.get("week", "")

    # Weekly reports
    base_weekly_qs = WeeklyReport.objects.filter(worker=worker).order_by('-week_start')
    if week_query:
        try:
            input_date = datetime.strptime(week_query, "%Y-%m-%d").date()
            sat = week_starting(input_date)
            base_weekly_qs = base_weekly_qs.filter(week_start=sat)
        except:
            pass

    # Weekly reports grouped by bhatta
    bhatta_weekly_list = []
    for bhatta in worker.bhattas.all():
        qs = base_weekly_qs.filter(bhatta=bhatta).order_by('-week_start')
        paginator = Paginator(qs, 10)
        page_number = request.GET.get(f'weekly_page_{bhatta.id}')
        page_obj = paginator.get_page(page_number)

        # Total bricks per bhatta
        total_bricks_bhatta = qs.aggregate(sum=Sum("bricks_worked"))["sum"] or 0

        # Append tuple (bhatta, page_obj, total_bricks_bhatta)
        bhatta_weekly_list.append((bhatta, page_obj, total_bricks_bhatta))

    # Advances
    adv_qs = Advance.objects.filter(worker=worker).order_by('-date')
    advances = Paginator(adv_qs, 10).get_page(request.GET.get("adv_page"))

    # Loans
    loan_qs = Loan.objects.filter(worker=worker).order_by('-date')
    loans = Paginator(loan_qs, 10).get_page(request.GET.get("loan_page"))

    # Settlements
    settle_qs = YearlySettlement.objects.filter(worker=worker).order_by('-year')
    settlements = Paginator(settle_qs, 10).get_page(request.GET.get("settle_page"))

    # Total bricks for worker
    total_bricks = base_weekly_qs.aggregate(sum=Sum("bricks_worked"))["sum"] or 0

    # Advance totals
    total_adv = adv_qs.aggregate(sum=Sum("amount"))["sum"] or 0
    total_adv_deducted = AdvanceDeduction.objects.filter(
        advance__worker=worker
    ).aggregate(sum=Sum("deducted_amount"))["sum"] or 0
    remaining_adv = total_adv - total_adv_deducted

    # Loan totals
    total_loan_taken = loan_qs.aggregate(sum=Sum("amount"))["sum"] or 0
    total_loan_deducted = LoanDeduction.objects.filter(
        loan__worker=worker
    ).aggregate(sum=Sum("deducted_amount"))["sum"] or 0
    remaining_loan = total_loan_taken - total_loan_deducted

    return render(request, 'worker/worker_detail.html', {
        "worker": worker,
        "week_query": week_query,
        "bhatta_weekly_list": bhatta_weekly_list,  # each tuple now has (bhatta, page_obj, total_bricks)
        "advances": advances,
        "loans": loans,
        "settlements": settlements,
        "total_bricks": total_bricks,
        "total_adv": remaining_adv,
        "total_loan": total_loan_taken,
        "total_loan_deducted": total_loan_deducted,
        "remaining_loan": remaining_loan,
    })







# ---------- Add Advance ----------
def add_advance(request, worker_id=None):
    """
    Simple add advance form. If worker_id provided, preselect the worker.
    """
    if request.method == 'POST':
        worker_pk = request.POST.get('worker')
        amount = request.POST.get('amount')
        date_str = request.POST.get('date')
        d = date_str or timezone.now().date()
        description = request.POST.get('description', '')
        Advance.objects.create(worker_id=worker_pk, amount=amount, date=d, description=description)
        # redirect to worker ledger detail if worker selected else to worker_ledger
        return redirect('worker:detail', worker_pk) if worker_pk else redirect('worker:worker_ledger')

    workers = Worker.objects.all()
    initial_worker = None
    if worker_id:
        initial_worker = get_object_or_404(Worker, pk=worker_id)
    return render(request, 'worker/add_advance.html', {'workers': workers, 'initial_worker': initial_worker})


# ---------- Add Loan ----------
def add_loan(request, worker_id=None):
    if request.method == 'POST':
        worker_pk = request.POST.get('worker')
        amount = request.POST.get('amount')
        date_str = request.POST.get('date')
        d = date_str or timezone.now().date()
        description = request.POST.get('description', '')
        Loan.objects.create(worker_id=worker_pk, amount=amount, date=d, description=description)
        return redirect('worker:detail', worker_pk) if worker_pk else redirect('worker:worker_ledger')

    workers = Worker.objects.all()
    initial_worker = None
    if worker_id:
        initial_worker = get_object_or_404(Worker, pk=worker_id)
    return render(request, 'worker/add_loan.html', {'workers': workers, 'initial_worker': initial_worker})
