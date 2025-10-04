from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def role_required(required_role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                try:
                    role = request.user.staff.role
                    if role == required_role:
                        return view_func(request, *args, **kwargs)
                    else:
                        return HttpResponseForbidden("You are not authorized to view this page.")
                except Exception:
                    return HttpResponseForbidden("Staff role not found.")
            return redirect('login')
        return wrapper
    return decorator

# Shortcut decorators for common roles
waiter_required = role_required('waiter')
cashier_required = role_required('cashier')
manager_required = role_required('manager')
admin_required = role_required('admin')
