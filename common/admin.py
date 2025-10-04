from django.contrib import admin
from . models import MenuItem,Table,Staff,Customer,Order,OrderItem,AssistanceRequest,Bill,Feedback,TaxSetting

# Register your models here.

admin.site.register(AssistanceRequest)
admin.site.register(Bill)
admin.site.register(Customer)
admin.site.register(Feedback)
admin.site.register(MenuItem)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Staff)
admin.site.register(Table)
admin.site.register(TaxSetting)
