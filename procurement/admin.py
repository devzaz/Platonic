from django.contrib import admin
from .models import *
# Register your models here.


class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ('description', 'purchase_order', 'quantity', 'unit_price', 'total_price')
    search_fields = ('description', 'purchase_order__po_id')
    list_filter = ('purchase_order__status',)
    list_per_page = 25



class StockItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity_on_hand', 'unit', 'is_stock_out', 'warehouse_location')
    search_fields = ('name',)
    list_filter = ('is_stock_out',)
    list_per_page = 25


admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderItem, PurchaseOrderItemAdmin)
admin.site.register(GoodsReceivedNote)
admin.site.register(StockItem, StockItemAdmin)
admin.site.register(VendorInvoice)