from django import forms
from common.models import MenuItem

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'category', 'meal_type', 'is_available', 'stock_quantity','low_stock_threshold']
