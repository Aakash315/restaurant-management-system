from django.urls import path
from . import views

urlpatterns = [
    path('', views.cashier_dashboard, name='cashier_dashboard'),
    path('bill/<int:bill_id>/', views.view_bill, name='view_bill'),
    path('finalize/<int:bill_id>/', views.finalize_bill, name='finalize_bill'),
    path('receipt/<int:bill_id>/', views.generate_receipt, name='generate_receipt'),
    path('paid-bills/', views.paid_bills, name='paid_bills'),
    path('show_bill/<int:bill_id>/', views.show_bill, name='show_bill'),


]