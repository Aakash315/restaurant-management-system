from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from common.models import Staff

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(user)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                print("Superuser logged in")
                return redirect('admin_dashboard')

            try:
                # Access role via related Staff model
                staff = Staff.objects.get(user=user)
                role = staff.role
            except Staff.DoesNotExist:
                return render(request, 'accounts/login.html')

            print(f"Login success: {user.username}, Role: {role}")


            if role == 'waiter':
                return redirect('waiter_dashboard')
            elif role == 'cashier':
                return redirect('cashier_dashboard')
            elif role == 'manager':
                return redirect('manager_dashboard')
            elif role == 'admin':
                return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials.')

    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
