from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Shipper)
admin.site.register(Supplier)
admin.site.register(Wish)
admin.site.register(Psm)
admin.site.register(Administrator)
admin.site.register(ProductPending)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderHistory)

