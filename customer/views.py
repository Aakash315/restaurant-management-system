from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from random import randint
from common.models import Table, Staff, MenuItem, Order, OrderItem,Customer,AssistanceRequest,Bill,Feedback
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
import random
from django.urls import reverse

def customer_register(request):
    if request.method == 'POST':
        name = request.POST['name']
        mobile = request.POST['mobile']
        email = request.POST['email']
        otp = str(randint(100000, 999999))

        customer = Customer.objects.create(name=name, mobile=mobile, email=email, otp=otp)
        send_mail(
            'Your OTP Code',
            f'Your OTP is: {otp}',
            'yourrestaurant@example.com',
            [email],
            fail_silently=False,
        )
        request.session['customer_id'] = customer.id
        return redirect('verify_otp')
    
    return render(request, 'customer/register.html')

def verify_otp(request):
    customer = Customer.objects.get(id=request.session['customer_id'])
    if request.method == 'POST':
        entered_otp = request.POST['otp']
        if entered_otp == customer.otp:
            customer.is_verified = True
            customer.save()
            return redirect('enter_members')

            # # Assign table
            # table = Table.objects.filter(is_occupied=False).first()
            # if not table:
            #     return render(request, 'customer/wait.html')

            # table.is_occupied = True
            # table.assigned_waiter = Staff.objects.filter(role='waiter').first()
            # table.save()
            # customer.table = table
            # customer.save()

            # return redirect('menu_view')
        else:
            return render(request, 'customer/verify_otp.html', {'error': 'Invalid OTP'})
    return render(request, 'customer/verify_otp.html')

def enter_members(request):
    customer = Customer.objects.get(id=request.session['customer_id'])

    if request.method == 'POST':
        num_members = int(request.POST['num_members'])

        # Find suitable table
        table = Table.objects.filter(is_occupied=False, capacity__gte=num_members).order_by('capacity').first()

        if not table:
            return render(request, 'customer/wait.html')  # No suitable table found

        # Assign table and waiter
        waiters = list(Staff.objects.filter(role='waiter'))
        if not waiters:
            return render(request, 'customer/wait.html', {'error': 'No waiter available at the moment.'})

        random_waiter = random.choice(waiters)
        table.is_occupied = True
        table.assigned_waiter = random_waiter
        table.save()

        customer.table = table
        customer.save()

        subject = 'Table Assigned - Mama\'s Kitchen'
        message = (
            f'Dear {customer.name},\n\n'
            f'Your table has been successfully reserved for {num_members} member(s).\n'
            f'Table Number: {table.id}\n'
            # f'Assigned Waiter: {random_waiter.name}\n\n'
            'Enjoy your meal at Mama\'s Kitchen!\n'
        )
        recipient_list = [customer.email]

        send_mail(
            subject,
            message,
            'yourrestaurant@example.com',
            recipient_list,
            fail_silently=False,
        )

        return redirect(f"{reverse('menu_view')}?meal_type=breakfast")

    return render(request, 'customer/enter_members.html') 

def menu_item_detail(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    return render(request, 'customer/menu_item_detail.html', {'item': item})


def menu_view(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer_register')
        
    customer = Customer.objects.get(id=customer_id)
    selected_meal_type = request.GET.get('meal_type') or request.session.get('last_selected_meal_type')
    items = MenuItem.objects.filter(is_available=True)
    menu_items = MenuItem.objects.filter(stock_quantity__gt=0)

    if selected_meal_type:
        items = items.filter(meal_type=selected_meal_type)
        request.session['last_selected_meal_type'] = selected_meal_type

    meal_types = dict(MenuItem.MEAL_TYPE_CHOICES)
    
    
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        menu_type = request.POST.get('meal_type')
        
        cart = request.session.get('cart', {})
        cart[item_id] = cart.get(item_id, 0) + quantity
        request.session['cart'] = cart

        if menu_type:
            return redirect(f'{reverse("menu_view")}?meal_type={menu_type}')

        return redirect('menu_view')
    
    cart = request.session.get('cart', {})
    return render(request, 'customer/menu.html', {
        'items': items,
        'cart': cart,
        'menu_items':menu_items,
        'meal_types': meal_types,
        'selected_meal_type': selected_meal_type
    })


def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    for item_id, quantity in cart.items():
        item = MenuItem.objects.get(id=item_id)
        item_total = item.price * quantity
        items.append({
            'item': item,
            'quantity': quantity,
            'total': item_total
        })
        total += item_total
    
    return render(request, 'customer/cart.html', {
        'items': items,
        'total': total
    })

@login_required
def increase_quantity(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)
    if item_id in cart:
        cart[item_id] += 1
    request.session['cart'] = cart
    return redirect('view_cart')

@login_required
def decrease_quantity(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)
    if item_id in cart:
        if cart[item_id] > 1:
            cart[item_id] -= 1
        else:
            cart.pop(item_id)  # remove if quantity goes below 1
    request.session['cart'] = cart
    return redirect('view_cart')


@login_required
def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    cart.pop(str(item_id), None)
    request.session['cart'] = cart
    return redirect('view_cart')

def place_order(request):
    customer = Customer.objects.get(id=request.session['customer_id'])
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('menu_view')
    
    order = Order.objects.create(
        table=customer.table,
        customer=customer,
        waiter=customer.table.assigned_waiter,
        status='Pending'
    )

    for item_id, quantity in cart.items():
        item = MenuItem.objects.get(id=item_id)
        OrderItem.objects.create(order=order, item=item, quantity=quantity)

    # Clear the cart
    request.session['cart'] = {}

    return render(request, 'customer/order_placed.html', {'order': order})


def request_assistance(request):
    customer = Customer.objects.get(id=request.session['customer_id'])
    table = customer.table

    if not table or not table.assigned_waiter:
        return render(request, 'customer/assistance_requested.html', {'error': 'No waiter assigned to your table.'})
    waiter = table.assigned_waiter

    # Check if there's already an unresolved request
    existing = AssistanceRequest.objects.filter(table=table, resolved=False).first()
    if not existing:
        AssistanceRequest.objects.create(table=table, waiter=waiter)

    return render(request, 'customer/assistance_requested.html')


def request_bill(request):
    customer = Customer.objects.get(id=request.session['customer_id'])
    order = Order.objects.filter(customer=customer).order_by('-created_at').first()

    if not order:
        return redirect('menu_view')
    
    # Create bill if not exists
    bill, created = Bill.objects.get_or_create(order=order, defaults={
        'total': sum([item.item.price * item.quantity for item in order.items.all()])
    })

    
    if bill.is_paid:
        table = customer.table
        if table:
            table.is_occupied = False
            table.assigned_waiter = None
            table.save()
        customer.table = None
        customer.save()


    return render(request, 'customer/request_bill.html', {
        'bill': bill,
        'order': order,
        'cgst': bill.cgst_amount(),
        'sgst': bill.sgst_amount(),
        'grand_total_with_tax': bill.grand_total_with_tax(),
    })

def submit_tip(request):
    customer = Customer.objects.get(id=request.session['customer_id'])
    order = Order.objects.filter(customer=customer).order_by('-created_at').first()
    bill = Bill.objects.get(order=order)

    if request.method == 'POST':
        tip_amount = Decimal(request.POST.get('tip', 0))
        bill.tip = tip_amount
        bill.save()

    return redirect('request_bill')


def order_status(request):
    customer = Customer.objects.get(id=request.session['customer_id'])
    order = Order.objects.filter(customer=customer).order_by('-created_at').first()

    if not order:
        return redirect('menu_view')

    return render(request, 'customer/order_status.html', {
        'order': order
    })


def leave_feedback(request):
    customer = Customer.objects.get(id=request.session['customer_id'])
    order = Order.objects.filter(customer=customer, bill__is_paid=True).order_by('-created_at').first()

    if not order:
        return redirect('menu_view')

    # Check if feedback already submitted
    if Feedback.objects.filter(order=order).exists():
        return render(request, 'customer/feedback_submitted.html')

    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')
        Feedback.objects.create(order=order, rating=rating, comment=comment)
        return redirect('leave_feedback')

    return render(request, 'customer/leave_feedback.html', {
        'order': order
    })
