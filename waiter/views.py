from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from common.models import AssistanceRequest, Table, Order, OrderItem,Staff
from django.http import HttpResponseNotFound
# from common.decorators import waiter_required

# @waiter_required
@login_required
def waiter_dashboard(request):
    try:
        waiter = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        return redirect('login') 

    requests = AssistanceRequest.objects.filter(waiter=waiter, resolved=False).order_by('-timestamp')
    return render(request, 'waiter/dashboard.html', {'requests': requests})


@login_required
def resolve_request(request, request_id):
    try:
        request_obj = get_object_or_404(AssistanceRequest, id=request_id)
        request_obj.resolved = True
        request_obj.save()
        return redirect('waiter_dashboard')
    except AssistanceRequest.DoesNotExist:
        return HttpResponseNotFound("Assistance request not found.")

@login_required
def waiter_orders(request):
    try:
        waiter = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        return redirect('login') 
    
    tables = Table.objects.filter(assigned_waiter=waiter, is_occupied=True)
    orders = Order.objects.filter(table__in=tables).order_by('-created_at')

    return render(request, 'waiter/orders.html', {
        'orders': orders
    })

@login_required
def mark_item_delivered(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)
    item.is_delivered = True
    item.save()
    return redirect('waiter_orders')

