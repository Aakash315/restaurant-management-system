from django.shortcuts import render, redirect, get_object_or_404
from common.models import OrderItem

def kitchen_dashboard(request):
    # Show all items with status not ready
    items = OrderItem.objects.filter(kitchen_status__in=['pending', 'preparing']).select_related('order__table', 'order__waiter')
    return render(request, 'kitchen/dashboard.html', {'items': items})

def update_kitchen_status(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)

    if item.kitchen_status == 'pending':
        item.kitchen_status = 'preparing'
    elif item.kitchen_status == 'preparing':
        item.kitchen_status = 'ready'

    item.save()
    return redirect('kitchen_dashboard')
