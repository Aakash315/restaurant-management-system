from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from common.decorators import role_required
from common.models import Table, Order, Feedback, Bill,MenuItem
from django.utils import timezone
from datetime import timedelta
from django.db import models
import csv
from django.http import HttpResponse
from datetime import datetime
from common.models import Bill
from django.db.models import Q

@login_required
def manager_dashboard(request):
    tables = Table.objects.all()
    orders = Order.objects.select_related('table', 'waiter').order_by('-created_at')[:10]
    return render(request, 'manager/dashboard.html', {
        'tables': tables,
        'orders': orders,
    })

@login_required
def feedback_list(request):
    feedbacks = Feedback.objects.select_related('order__table').order_by('-created_at')
    return render(request, 'manager/feedback.html', {
        'feedbacks': feedbacks,
    })

@login_required
def daily_report(request):
    today = timezone.now().date()
    bills_today = Bill.objects.filter(generated_at__date=today, is_paid=True)

    total_revenue = sum(b.total for b in bills_today)
    total_tips = sum(b.tip for b in bills_today)
    order_count = bills_today.count()

    return render(request, 'manager/report.html', {
        'total_revenue': total_revenue,
        'total_tips': total_tips,
        'order_count': order_count,
        'bills': bills_today,
        'date': today,
    })

@login_required
def inventory_dashboard(request):
    query = request.GET.get('q', '')
    items = MenuItem.objects.all()

    if query:
        items = items.filter(name__icontains=query)


    low_stock_items = items.filter(stock_quantity__lte=models.F('low_stock_threshold'))

    return render(request, 'manager/inventory.html', {
        'items': items,
        'low_stock_items': low_stock_items,
        'query':query
    })

@login_required
def update_stock(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    if request.method == 'POST':
        new_qty = int(request.POST.get('stock_quantity'))
        item.stock_quantity = new_qty
        item.save()
    return redirect('inventory_dashboard')


@login_required
def export_daily_report_csv(request):
    today = timezone.now().date()
    bills = Bill.objects.filter(is_paid=True, generated_at__date=today)

    response = HttpResponse(content_type='text/csv')
    filename = f"sales_report_{today}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['Bill ID', 'Table', 'Waiter', 'Total', 'Tip', 'Final Total', 'Payment Method', 'Paid At'])

    for bill in bills:
        writer.writerow([
            bill.id,
            bill.order.table.number,
            bill.order.waiter.user.username if bill.order.waiter else 'N/A',
            f"{bill.total:.2f}",
            f"{bill.tip:.2f}",
            f"{bill.final_total():.2f}",
            bill.payment_method,
            bill.generated_at.strftime('%Y-%m-%d %H:%M'),
        ])

    return response

