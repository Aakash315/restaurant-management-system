from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from common.models import Staff
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        try:
            staff = Staff.objects.get(user=request.user)
            role = staff.role
            if role == 'waiter':
                return redirect('waiter_dashboard')
            elif role == 'cashier':
                return redirect('cashier_dashboard')
            elif role == 'manager':
                return redirect('manager_dashboard')
            elif role == 'admin':
                return redirect('admin_dashboard')
        except Staff.DoesNotExist:
            pass
        
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


@login_required
def change_password_view(request):
    try:
        staff = Staff.objects.get(user=request.user)
        allowed_roles = ['manager', 'cashier', 'admin', 'waiter']

        if staff.role not in allowed_roles:
            messages.error(request, "You do not have permission to change the password.")
            return redirect('login')

    except Staff.DoesNotExist:
        messages.error(request, "Staff role not assigned.")
        return redirect('login')

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in after password change
            messages.success(request, 'Your password was successfully updated!')

            if user.email:
                send_mail(
                    subject='Password Changed Successfully',
                    message=(
                        f"Hello {user.get_full_name() or user.username},\n\n"
                        "Your password has been successfully changed. "
                        "If you did not make this change, please contact support immediately."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,  # avoid crashing if email fails
                )

            # Role-based redirect
            role = staff.role
            if role == 'manager':
                return redirect('manager_dashboard')
            elif role == 'cashier':
                return redirect('cashier_dashboard')
            elif role == 'admin':
                return redirect('admin_dashboard')
            elif role == 'waiter':
                return redirect('waiter_dashboard')

            # fallback redirect if none match
            return redirect('login')

        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'accounts/change_password.html', {'form': form})

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Check if user is staff and has role in Staff model
            if not hasattr(user, 'staff'):
                messages.error(request, "User with this email is not staff.")
                return render(request, 'accounts/forgot_password.html')

            # Generate token and uid
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Build password reset link
            reset_link = request.build_absolute_uri(f'/accounts/reset-password/{uid}/{token}/')


            # Send email (customize as needed)
            subject = "Password Reset Request"
            message = render_to_string('accounts/password_reset_email.html', {
                'user': user,
                'reset_link': reset_link,
            })
            send_mail(subject, message, 'no-reply@example.com', [user.email])

            messages.success(request, "Password reset email sent. Check your inbox.")
            return redirect('login')

        except User.DoesNotExist:
            messages.error(request, "No user found with this email.")
    
    return render(request, 'accounts/forgot_password.html')

def reset_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                # update_session_auth_hash(request, user)  # Keep user logged in after reset
                messages.success(request, "Password has been reset successfully.")
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'accounts/reset_password.html', {'form': form})
    else:
        messages.error(request, "The password reset link is invalid or has expired.")
        return redirect('forgot_password')