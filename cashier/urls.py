from django.urls import path
from . import views

urlpatterns = [
    path('', views.cashier_dashboard, name='cashier_dashboard'),
    path('bill/<int:bill_id>/', views.view_bill, name='view_bill'),
    path('finalize/<int:bill_id>/', views.finalize_bill, name='finalize_bill'),
    path('receipt/<int:bill_id>/', views.generate_receipt, name='generate_receipt'),

]