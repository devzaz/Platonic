from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sales.models import Contact
from .models import PurchaseOrder, PurchaseOrderItem, VendorInvoice, StockItem
from django.http import JsonResponse

from django.db.models import Sum, Value, Q, DecimalField, F, ExpressionWrapper
from django.db.models.functions import Coalesce
from decimal import Decimal


from django.shortcuts import get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder



@login_required
def index(request):
    total_stock_out = StockItem.objects.filter(is_stock_out=True).count()
    context = {
        'total_stock_out': total_stock_out
    }
    return render(request, 'procurement/index.html', context)



def vendors_api(request):

    vendors = list(Contact.objects
                   .filter(contact_type='supplier')
                   .annotate(
                      total_invoiced = Coalesce(
                          Sum('vendorinvoice__total_amount', filter=Q(vendorinvoice__status='paid')),
                          Value(Decimal('0.00')),
                            output_field=DecimalField(max_digits=12, decimal_places=2)
                      ), 
                   )
                   .values(
        'name', 'performance_rating', 'total_invoiced', 'contact_id'     
    ))
    return JsonResponse({'vendors': vendors})


def vendor_detail_api(request, pk):
    v = get_object_or_404(Contact, contact_id=pk, contact_type='supplier')
    pos_qs = PurchaseOrder.objects.filter(vendor=v).select_related('project')


    data = {
        'contact':{
            'id':str(v.contact_id),
            'name':v.name,
            'email':v.email,
            'phone': v.phone,
            'rating': v.performance_rating,

        },

        'purchase_orders':[
            {
                'id': po.po_id,
                'project': po.project.name if po.project_id else '',
                'total':0

            }
            for po in pos_qs
        ],
    }
    return JsonResponse(data,encoder=DjangoJSONEncoder)



def purchase_order_api(request):

    total_line_expr = ExpressionWrapper(
        F('items__unit_price') * F('items__quantity'),
        output_field=DecimalField(max_digits=12, decimal_places=2)
    )



    pos = list(PurchaseOrder.objects.select_related('vendor', 'project')
               .annotate(
                   total_amount=Coalesce(
                       Sum(total_line_expr),
                       Value(Decimal('0.00')),
                       output_field=DecimalField(max_digits=12, decimal_places=2)
                   )
               )
               .values(
                   'po_id', 'vendor__name', 'project__name', 'order_date', 'status', 'total_amount'
               )
               .order_by('-order_date')
               )
    return JsonResponse({'purchase_orders': pos})




def invoice_list_api(request):
    invoices = list(VendorInvoice.objects.select_related('vendor', 'purchase_order')
                    .values(
                        "invoice_id","purchase_order__po_id", "vendor__name", "invoice_date", "total_amount" , "status"
                    ))
    
    return JsonResponse({'invoices': invoices})




def stock_item_api(request):
    stock_items = list(
        StockItem.objects.all()
        .values(
            "name", "quantity_on_hand", "unit", "warehouse_location", "is_stock_out"
        )
    )

    return JsonResponse({'stock':stock_items})






