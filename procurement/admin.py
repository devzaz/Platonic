from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderItem)
admin.site.register(GoodsReceivedNote)
admin.site.register(StockItem)
admin.site.register(VendorInvoice)