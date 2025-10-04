from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Table(models.Model):
    number = models.IntegerField(unique=True)
    capacity = models.IntegerField()
    is_occupied = models.BooleanField(default=False)
    assigned_waiter = models.ForeignKey('Staff', null=True, blank=True, on_delete=models.SET_NULL)
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Table {self.number}-{self.assigned_waiter}"

class Staff(models.Model):
    ROLE_CHOICES = (
        ('waiter', 'Waiter'),
        ('cashier', 'Cashier'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user} - {self.role}"

class Customer(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    table = models.ForeignKey(Table, null=True, blank=True, on_delete=models.SET_NULL)

class MenuItem(models.Model):
    CATEGORY_CHOICES = (
        ('Veg', 'Vegetarian'),
        ('Non-Veg', 'Non-Vegetarian'),
    )

    MEAL_TYPE_CHOICES = (
        ('burgers', 'Burgers'),
        ('pizzas', 'Pizzas'),
        ('salads', 'Salads'),
        ('breakfast', 'Breakfast'),
        ('starter', 'Starter'),
        ('soup', 'Soup'),
        ('main_course', 'Main Course'),
        ('rice', 'Rice'),
        ('noodles', 'Noodles'),
        ('dessert', 'Dessert'),
        ('juices', 'Juices'),
        ('beverage', 'Beverage'),
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES,default="Veg")
    stock_quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    meal_type = models.CharField(max_length=50, choices=MEAL_TYPE_CHOICES, default='main_course')

    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold

    def is_out_of_stock(self):
        return self.stock_quantity <= 0

    def __str__(self):
        return self.name

class Order(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    waiter = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')  # e.g. pending, preparing, served, paid
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_delivered = models.BooleanField(default=False)

    KITCHEN_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
    ]
    kitchen_status = models.CharField(max_length=15, choices=KITCHEN_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.quantity}*{self.item.name} ({'Delivered' if self.is_delivered else 'Pending'})"
    
    @property
    def total_price(self):
        return self.item.price * self.quantity

class AssistanceRequest(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    waiter = models.ForeignKey(Staff, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Request from Table {self.table.number} - Resolved: {self.resolved}"

class Bill(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    tip = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=10, blank=True, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def final_total(self):
        return self.total + self.tip 
    
    def get_tax_settings(self):
        return TaxSetting.objects.last()
    
    def cgst_amount(self):
        setting = self.get_tax_settings()
        if not setting:
            return Decimal('0.00')
        return self.total * setting.cgst / Decimal('100.0')

    def sgst_amount(self):
        setting = self.get_tax_settings()
        if not setting:
            return Decimal('0.00')
        return self.total * setting.sgst / Decimal('100.0')

    def grand_total_with_tax(self):
        return self.final_total() + self.cgst_amount() + self.sgst_amount()
    
class Feedback(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for Table {self.order.table.number} - {self.rating}★"
    
class TaxSetting(models.Model):
    cgst = models.DecimalField(max_digits=5, decimal_places=2)
    sgst = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"CGST: {self.cgst}%, SGST: {self.sgst}%"
