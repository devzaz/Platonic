from django.urls import path
from .views import index, vendors_api, vendor_detail_api, purchase_order_api, invoice_list_api, stock_item_api


urlpatterns = [
    path('procurement_home/', index, name='procurement_home'),


    path('api/vendors/', vendors_api, name='vendors_api'),
    path('api/vendors/<uuid:pk>', vendor_detail_api, name='vendor_detail'),

    path('api/po/', purchase_order_api, name='purchase_order_api'),
    path('api/invoices/', invoice_list_api, name='invoice_list_api'),
    path('api/stock/', stock_item_api, name='stock_item_api'),
]
