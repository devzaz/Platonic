from django.shortcuts import render
from django.http import JsonResponse
from .models import Project

from datetime import date
from django.db.models import Sum, Case, When, DecimalField, F, Value, DateField, Q
from django.db.models.functions import Coalesce, TruncMonth
from decimal import Decimal


from .models import Project, FinancialTransaction
from core.models import ChartOfAccounts

from django.utils.dateparse import parse_date

# Create your views here.


CASH_CODES = ['1010-001', '1010-002']

DECIMAL_T = DecimalField(max_digits=14, decimal_places=2)
D0 = Value(Decimal('0.00'), output_field=DECIMAL_T)


def project_api(request):
    data = list(Project.objects.values(
        'name', 'project_manager__username', 'status', 'progress', 'budget'
    ))
    return JsonResponse({'projects':data})


def _first_of_month(d: date) -> date:
    return date(d.year, d.month, 1)

def _add_months(d: date, months: int) -> date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    return date(y, m, 1)

def cashflow_api(request):
    try:
        months = max(1, int(request.GET.get('months') or 6))
    except (TypeError, ValueError):
        months = 6
    settled_only = str(request.GET.get('settled', '0')).lower() in ('1', 'true', 'yes', 'y')

    today = date.today()
    start = _add_months(_first_of_month(today), -(months - 1))
    end = today

    cash_accts = ChartOfAccounts.objects.filter(code__in=CASH_CODES, is_active=True)

    qs = FinancialTransaction.objects.filter(
        status='approved',
        account__in=cash_accts,
        transaction_date__gte=start,
        transaction_date__lte=end,
    )
    if settled_only:
        qs = qs.filter(is_received=True)

    monthly = (
        qs.annotate(m=TruncMonth('transaction_date', output_field=DateField()))  # <- ensure date
          .values('m')
          .annotate(
              cash_in=Coalesce(
                  Sum(Case(When(is_debit=True, then=F('amount')),
                           default=D0, output_field=DECIMAL_T),
                      output_field=DECIMAL_T),
                  D0, output_field=DECIMAL_T
              ),
              cash_out=Coalesce(
                  Sum(Case(When(is_debit=False, then=F('amount')),
                           default=D0, output_field=DECIMAL_T),
                      output_field=DECIMAL_T),
                  D0, output_field=DECIMAL_T
              ),
          )
          .order_by('m')
    )

    # Build continuous month buckets
    labels, ins, outs = [], [], []
    rows_by_month = {row['m']: row for row in monthly}   # <- no .date()

    cur = _first_of_month(start)
    for _ in range(months):
        labels.append(cur.strftime('%b %Y'))
        row = rows_by_month.get(cur)
        ins.append(float(row['cash_in']) if row else 0.0)
        outs.append(float(row['cash_out']) if row else 0.0)
        cur = _add_months(cur, 1)

    return JsonResponse({
        'labels': labels,
        'cash_in': ins,
        'cash_out': outs,
        'params': {'months': months, 'settled_only': settled_only},
        'cash_accounts': CASH_CODES,
    })




def revenue_profit_api(request):
    """
    mode=single  -> ignore debit/credit; sum amounts by category (better for single-entry workflows)
    mode=gaap    -> use debit/credit signs (debit EXPENSE/COGS = +, credit = - ; credit REVENUE = +, debit = -)
    """
    # params
    try:
        months = max(1, int(request.GET.get('months') or 6))
    except (TypeError, ValueError):
        months = 6
    settled_only = str(request.GET.get('settled', '0')).lower() in ('1', 'true', 'yes', 'y')
    mode = (request.GET.get('mode') or 'single').lower()

    today = date.today()
    start = _add_months(_first_of_month(today), -(months - 1))
    end = today

    qs = FinancialTransaction.objects.filter(
        status='approved',
        transaction_date__gte=start,
        transaction_date__lte=end,
        account__isnull=False,
        account__category__in=['REVENUE', 'COGS', 'EXPENSE'],
    )
    if settled_only:
        qs = qs.filter(is_received=True)

    base = qs.annotate(m=TruncMonth('transaction_date', output_field=DateField())).values('m')

    if mode == 'gaap':
        # Use accounting signs
        monthly = (
            base.annotate(
                revenue=Coalesce(
                    Sum(Case(
                        When(account__category='REVENUE', is_debit=False, then=F('amount')),
                        When(account__category='REVENUE', is_debit=True,  then=-F('amount')),
                        default=D0, output_field=DECIMAL_T
                    ), output_field=DECIMAL_T),
                    D0, output_field=DECIMAL_T
                ),
                cogs=Coalesce(
                    Sum(Case(
                        When(account__category='COGS', is_debit=True,  then=F('amount')),
                        When(account__category='COGS', is_debit=False, then=-F('amount')),
                        default=D0, output_field=DECIMAL_T
                    ), output_field=DECIMAL_T),
                    D0, output_field=DECIMAL_T
                ),
                opex=Coalesce(
                    Sum(Case(
                        When(account__category='EXPENSE', is_debit=True,  then=F('amount')),
                        When(account__category='EXPENSE', is_debit=False, then=-F('amount')),
                        default=D0, output_field=DECIMAL_T
                    ), output_field=DECIMAL_T),
                    D0, output_field=DECIMAL_T
                ),
            ).order_by('m')
        )
    else:
        # SINGLE-ENTRY friendly: ignore debit/credit
        monthly = (
            base.annotate(
                revenue=Coalesce(Sum(Case(
                    When(account__category='REVENUE', then=F('amount')),
                    default=D0, output_field=DECIMAL_T
                ), output_field=DECIMAL_T), D0, output_field=DECIMAL_T),
                cogs=Coalesce(Sum(Case(
                    When(account__category='COGS', then=F('amount')),
                    default=D0, output_field=DECIMAL_T
                ), output_field=DECIMAL_T), D0, output_field=DECIMAL_T),
                opex=Coalesce(Sum(Case(
                    When(account__category='EXPENSE', then=F('amount')),
                    default=D0, output_field=DECIMAL_T
                ), output_field=DECIMAL_T), D0, output_field=DECIMAL_T),
            ).order_by('m')
        )

    rows = {row['m']: row for row in monthly}
    labels, revenue_arr, profit_arr, debug_cogs, debug_opex = [], [], [], [], []

    cur = _first_of_month(start)
    for _ in range(months):
        labels.append(cur.strftime('%b %Y'))
        row = rows.get(cur)
        rev  = float(row['revenue']) if row else 0.0
        cgs  = float(row['cogs'])    if row else 0.0
        opx  = float(row['opex'])    if row else 0.0
        revenue_arr.append(rev)
        profit_arr.append(rev - (cgs + opx))
        debug_cogs.append(cgs)
        debug_opex.append(opx)
        cur = _add_months(cur, 1)

    return JsonResponse({
        'labels': labels,
        'revenue': revenue_arr,
        'profit': profit_arr,
        'components': {'cogs': debug_cogs, 'opex': debug_opex},
        'params': {'months': months, 'settled_only': settled_only, 'mode': mode},
    })




def project_profitability_api(request):
    """
    Returns per-project revenue/COGS/opex and profit for a period.

    Query params:
      - from: YYYY-MM-DD   (optional; if omitted, uses months)
      - to:   YYYY-MM-DD   (optional; default today)
      - months: int        (default 6, used if no from/to)
      - settled: 1/0       (default 0)
      - mode: single|gaap  (default single)
      - limit: int         (default 8)
      - order_by: profit|revenue|cost (default profit)
    """
    # ---- period ----
    raw_from = request.GET.get('from')
    raw_to   = request.GET.get('to')
    if raw_from or raw_to:
        start = parse_date(raw_from) if raw_from else _first_of_month(date.today())
        end   = parse_date(raw_to)   if raw_to   else date.today()
    else:
        try:
            months = max(1, int(request.GET.get('months') or 6))
        except (TypeError, ValueError):
            months = 6
        today = date.today()
        start = _add_months(_first_of_month(today), -(months - 1))
        end   = today

    # ---- other params ----
    settled_only = str(request.GET.get('settled', '0')).lower() in ('1', 'true', 'yes', 'y')
    mode = (request.GET.get('mode') or 'single').lower()
    try:
        limit = max(1, int(request.GET.get('limit') or 8))
    except (TypeError, ValueError):
        limit = 8
    order_by = (request.GET.get('order_by') or 'profit').lower()
    if order_by not in ('profit', 'revenue', 'cost'):
        order_by = 'profit'

    # ---- base queryset ----
    qs = (FinancialTransaction.objects
          .filter(status='approved',
                  transaction_date__gte=start,
                  transaction_date__lte=end,
                  account__isnull=False,
                  account__category__in=['REVENUE', 'COGS', 'EXPENSE'])
          .select_related('project', 'account'))

    if settled_only:
        qs = qs.filter(is_received=True)

    # ---- aggregate per project ----
    base = qs.values('project_id', 'project__name')

    if mode == 'gaap':
        # Use accounting signs
        per_project = (
            base.annotate(
                revenue=Coalesce(Sum(Case(
                    When(account__category='REVENUE', is_debit=False, then=F('amount')),
                    When(account__category='REVENUE', is_debit=True,  then=-F('amount')),
                    default=D0, output_field=DECIMAL_T
                ), output_field=DECIMAL_T), D0, output_field=DECIMAL_T),
                cogs=Coalesce(Sum(Case(
                    When(account__category='COGS', is_debit=True,  then=F('amount')),
                    When(account__category='COGS', is_debit=False, then=-F('amount')),
                    default=D0, output_field=DECIMAL_T
                ), output_field=DECIMAL_T), D0, output_field=DECIMAL_T),
                opex=Coalesce(Sum(Case(
                    When(account__category='EXPENSE', is_debit=True,  then=F('amount')),
                    When(account__category='EXPENSE', is_debit=False, then=-F('amount')),
                    default=D0, output_field=DECIMAL_T
                ), output_field=DECIMAL_T), D0, output_field=DECIMAL_T),
            )
        )
    else:
        # SINGLE-ENTRY friendly: ignore debit/credit, sum by category
        per_project = (
            base.annotate(
                revenue=Coalesce(Sum(Case(
                    When(account__category='REVENUE', then=F('amount')),
                    default=D0, output_field=DECIMAL_T
                ), output_field=DECIMAL_T), D0, output_field=DECIMAL_T),
                cogs=Coalesce(Sum(Case(
                    When(account__category='COGS', then=F('amount')),
                    default=D0, output_field=DECIMAL_T
                ), output_field=DECIMAL_T), D0, output_field=DECIMAL_T),
                opex=Coalesce(Sum(Case(
                    When(account__category='EXPENSE', then=F('amount')),
                    default=D0, output_field=DECIMAL_T
                ), output_field=DECIMAL_T), D0, output_field=DECIMAL_T),
            )
        )

    rows = []
    for r in per_project:
        rev  = float(r['revenue'] or 0.0)
        cgs  = float(r['cogs']    or 0.0)
        opx  = float(r['opex']    or 0.0)
        profit = rev - (cgs + opx)
        rows.append({
            'project_id':   r['project_id'],
            'project_name': r['project__name'],
            'revenue': rev, 'cogs': cgs, 'opex': opx, 'profit': profit,
            'cost': cgs + opx,
        })

    # ---- sort & limit ----
    rows.sort(key=lambda x: x[order_by], reverse=True)
    rows = rows[:limit]

    labels = [r['project_name'] for r in rows]
    revenue = [r['revenue'] for r in rows]
    cost = [r['cost'] for r in rows]
    profit = [r['profit'] for r in rows]

    return JsonResponse({
        'labels': labels,
        'revenue': revenue,
        'cost': cost,
        'profit': profit,
        'params': {
            'from': start.isoformat(), 'to': end.isoformat(),
            'settled_only': settled_only, 'mode': mode,
            'limit': limit, 'order_by': order_by
        }
    })





# Optional: if you keep canonical AR/AP codes in your CoA, put them here.
AR_CODES = []  # e.g. ['1200-001']
AP_CODES = []  # e.g. ['2000-001']

def kpis_api(request):
    """
    Returns:
      - gross_revenue_ytd
      - net_profit_ytd  (Revenue - (COGS + OPEX))
      - open_ar         (Accounts Receivable balance; falls back to pending revenue)
      - open_ap         (Accounts Payable balance;  falls back to pending expenses)
    Params:
      - mode: single|gaap  (default single)
      - settled: 1/0       (only count transactions with is_received=True)
      - year: int          (default: current year)
    """
    mode = (request.GET.get('mode') or 'single').lower()
    settled_only = str(request.GET.get('settled', '0')).lower() in ('1','true','yes','y')
    try:
        year = int(request.GET.get('year') or date.today().year)
    except ValueError:
        year = date.today().year

    start = date(year, 1, 1)
    end   = date.today()

    # Base YTD queryset
    base_ytd = FinancialTransaction.objects.filter(
        status='approved',
        transaction_date__gte=start,
        transaction_date__lte=end,
        account__isnull=False,
        account__category__in=['REVENUE','COGS','EXPENSE'],
    )
    if settled_only:
        base_ytd = base_ytd.filter(is_received=True)

    # ---- Revenue / COGS / OPEX (two modes) ----
    if mode == 'gaap':
        # Use accounting signs
        agg = base_ytd.aggregate(
            revenue=Coalesce(Sum(Case(
                When(account__category='REVENUE', is_debit=False, then=F('amount')),
                When(account__category='REVENUE', is_debit=True,  then=-F('amount')),
                default=D0, output_field=DECIMAL_T
            ), output_field=DECIMAL_T), D0, output_field=DECIMAL_T),
            cogs=Coalesce(Sum(Case(
                When(account__category='COGS', is_debit=True,  then=F('amount')),
                When(account__category='COGS', is_debit=False, then=-F('amount')),
                default=D0, output_field=DECIMAL_T
            ), output_field=DECIMAL_T), D0, output_field=DECIMAL_T),
            opex=Coalesce(Sum(Case(
                When(account__category='EXPENSE', is_debit=True,  then=F('amount')),
                When(account__category='EXPENSE', is_debit=False, then=-F('amount')),
                default=D0, output_field=DECIMAL_T
            ), output_field=DECIMAL_T), D0, output_field=DECIMAL_T),
        )
    else:
        # SINGLE-ENTRY friendly: ignore debit/credit; sum by category
        agg = base_ytd.aggregate(
            revenue=Coalesce(Sum(Case(
                When(account__category='REVENUE', then=F('amount')),
                default=D0, output_field=DECIMAL_T
            ), output_field=DECIMAL_T), D0, output_field=DECIMAL_T),
            cogs=Coalesce(Sum(Case(
                When(account__category='COGS', then=F('amount')),
                default=D0, output_field=DECIMAL_T
            ), output_field=DECIMAL_T), D0, output_field=DECIMAL_T),
            opex=Coalesce(Sum(Case(
                When(account__category='EXPENSE', then=F('amount')),
                default=D0, output_field=DECIMAL_T
            ), output_field=DECIMAL_T), D0, output_field=DECIMAL_T),
        )

    gross_revenue_ytd = float(agg['revenue'] or 0)
    cost_ytd = float(agg['cogs'] or 0) + float(agg['opex'] or 0)
    net_profit_ytd = gross_revenue_ytd - cost_ytd

    # ---- Open AR/AP (ledger first; fallback to pending flags) ----
    # Find AR/AP accounts by code OR by name (fallback)
    ar_accounts = ChartOfAccounts.objects.filter(
        Q(code__in=AR_CODES) |
        (Q(category='ASSET') & Q(name__icontains='receiv'))
    )
    ap_accounts = ChartOfAccounts.objects.filter(
        Q(code__in=AP_CODES) |
        (Q(category='LIABILITY') & Q(name__icontains='payable'))
    )

    # Current open balances (to date) regardless of year window
    # AR (asset): balance = debits - credits
    ar_qs = FinancialTransaction.objects.filter(
        status='approved',
        account__in=ar_accounts
    )
    if settled_only:
        ar_qs = ar_qs.filter(is_received=True)

    ap_qs = FinancialTransaction.objects.filter(
        status='approved',
        account__in=ap_accounts
    )
    if settled_only:
        ap_qs = ap_qs.filter(is_received=True)

    ar_bal = ar_qs.aggregate(
        bal=Coalesce(Sum(Case(
            When(is_debit=True,  then=F('amount')),
            When(is_debit=False, then=-F('amount')),
            default=D0, output_field=DECIMAL_T
        ), output_field=DECIMAL_T), D0, output_field=DECIMAL_T)
    )['bal'] or Decimal('0.00')

    # AP (liability): balance = credits - debits
    ap_bal = ap_qs.aggregate(
        bal=Coalesce(Sum(Case(
            When(is_debit=False, then=F('amount')),  # credit increases AP
            When(is_debit=True,  then=-F('amount')),
            default=D0, output_field=DECIMAL_T
        ), output_field=DECIMAL_T), D0, output_field=DECIMAL_T)
    )['bal'] or Decimal('0.00')

    # Fallback if ledger isn’t used: “open” = approved but not received/paid
    if ar_bal == 0:
        ar_fallback = FinancialTransaction.objects.filter(
            status='approved',
            is_received=False,
            account__category='REVENUE'
        ).aggregate(
            amt=Coalesce(Sum(F('amount'), output_field=DECIMAL_T), D0, output_field=DECIMAL_T)
        )['amt'] or Decimal('0.00')
        ar_bal = ar_fallback

    if ap_bal == 0:
        ap_fallback = FinancialTransaction.objects.filter(
            status='approved',
            is_received=False,
            account__category__in=['COGS','EXPENSE']
        ).aggregate(
            amt=Coalesce(Sum(F('amount'), output_field=DECIMAL_T), D0, output_field=DECIMAL_T)
        )['amt'] or Decimal('0.00')
        ap_bal = ap_fallback

    return JsonResponse({
        'gross_revenue_ytd': float(gross_revenue_ytd),
        'net_profit_ytd': float(net_profit_ytd),
        'open_ar': float(ap_bal if False else ar_bal),  # keep as AR; (typo guard)
        'open_ap': float(ap_bal),
        'mode': mode,
        'settled_only': settled_only,
        'year': year
    })