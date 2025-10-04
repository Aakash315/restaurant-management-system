from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from common.decorators import role_required
from common.models import MenuItem,Staff,Table,TaxSetting
from . forms import MenuItemForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

# @role_required(['admin'])
@login_required
def admin_dashboard(request):
    return render(request, 'adminpanel/dashboard.html')


@login_required
def menu_management(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    meal_type = request.GET.get('meal_type')

    items = MenuItem.objects.all()

    if query:
        items = items.filter(name__icontains=query)

    if category:
        items = items.filter(category__iexact=category)  # assuming field name is 'category'

    if meal_type:
        items = items.filter(meal_type__iexact=meal_type)  # assuming field name is 'meal_type'

    return render(request, 'adminpanel/menu_management.html', {
        'items': items,
        'query': query,
        'category': category,
        'meal_type': meal_type,
    })

@login_required
def add_menu_item(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('menu_management')
    else:
        form = MenuItemForm()

    return render(request, 'adminpanel/add_menu_item.html', {
        'form': form
    })


@login_required
def edit_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)

    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('menu_management')
    else:
        form = MenuItemForm(instance=item)

    return render(request, 'adminpanel/edit_menu_item.html', {
        'form': form,
        'item': item
    })

@login_required
def delete_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    item.delete()
    return redirect('menu_management')


@login_required
def table_config(request):
    tables = Table.objects.all()
    waiters = Staff.objects.filter(role='waiter')

    if request.method == 'POST':
        table_id = request.POST.get('table_id')
        waiter_id = request.POST.get('waiter_id')
        capacity = request.POST.get('capacity')
        is_occupied = request.POST.get('is_occupied') == 'on'

        try:
            table = Table.objects.get(id=table_id)
            if waiter_id:
                table.assigned_waiter = Staff.objects.get(id=waiter_id)
            else:
                table.assigned_waiter = None
            table.capacity = capacity
            table.is_occupied = is_occupied
            table.save()
            messages.success(request, f"Table {table.number} updated successfully.")
        except Table.DoesNotExist:
            messages.error(request, "Table not found.")
        except Staff.DoesNotExist:
            messages.error(request, "Waiter not found.")
        return redirect('table_config')

    return render(request, 'adminpanel/table_config.html', {
        'tables': tables,
        'waiters': waiters,
    })

@login_required
def user_management(request):
    staff_members = Staff.objects.select_related('user').all()

    if request.method == 'POST':
        action = request.POST.get('action')
        staff_id = request.POST.get('staff_id')

        try:
            staff = Staff.objects.get(id=staff_id)
            user = staff.user

            if action == 'change_role':
                new_role = request.POST.get('role')
                staff.role = new_role
                staff.save()
                messages.success(request, f"{user.username}'s role updated to {new_role}.")

            elif action == 'toggle_active':
                user.is_active = not user.is_active
                user.save()
                status = "activated" if user.is_active else "deactivated"
                messages.success(request, f"{user.username} has been {status}.")

            elif action == 'delete_user':
                username = user.username
                user.delete()
                messages.success(request, f"User {username} has been deleted.")

        except Staff.DoesNotExist:
            messages.error(request, "Staff member not found.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return redirect('user_management')

    return render(request, 'adminpanel/user_management.html', {
        'staff_members': staff_members,
    })


@login_required
def add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')

        if not all([username, password, email, role]):
            messages.error(request, "All fields are required.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            try:
                user = User.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=make_password(password),
                    is_active=True
                )
                Staff.objects.create(user=user, role=role)
                messages.success(request, f"User '{username}' created successfully.")
                return redirect('user_management')
            except Exception as e:
                messages.error(request, f"Error creating user: {str(e)}")

    return render(request, 'adminpanel/add_user.html')


@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    staff = get_object_or_404(Staff, user=user)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        password = request.POST.get('password')

        # Basic validation
        if not all([username, email, role]):
            messages.error(request, "Username, email, and role are required.")
        elif User.objects.exclude(id=user.id).filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            if password:
                user.password = make_password(password)
            user.save()

            staff.role = role
            staff.save()

            messages.success(request, f"User '{username}' updated successfully.")
            return redirect('user_management')

    return render(request, 'adminpanel/edit_user.html', {
        'user_obj': user,
        'staff': staff
    })

@login_required
def add_table(request):
    if request.method == 'POST':
        number = request.POST.get('number')
        capacity = request.POST.get('capacity')

        if not number or not capacity:
            messages.error(request, "Both table number and capacity are required.")
        elif Table.objects.filter(number=number).exists():
            messages.error(request, f"Table number {number} already exists.")
        else:
            Table.objects.create(number=number, capacity=capacity)
            messages.success(request, f"Table {number} created successfully.")
            return redirect('table_config')

    return render(request, 'adminpanel/add_table.html')


@login_required
def tax_settings(request):
    tax_data = TaxSetting.objects.first()  # Only one instance expected

    if request.method == 'POST':
        cgst = request.POST.get('cgst')
        sgst = request.POST.get('sgst')

        if tax_data:
            tax_data.cgst = cgst
            tax_data.sgst = sgst
            tax_data.save()
        else:
            TaxSetting.objects.create(cgst=cgst, sgst=sgst)

        return redirect('admin_dashboard')
    return render(request, 'adminpanel/tax_settings.html', {'tax_data': tax_data})
