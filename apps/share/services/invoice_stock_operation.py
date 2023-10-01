from apps.share.services.stock_manager import StockManager
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from apps.inventories.models.stock import Stock
import sys
from datetime import date
def get_invoice_item_stock(tenant, item, warehouse_id):
    item_id = item['item_id']
    uom_id= item['unit']
    qty = item['qty']
    current_date = date.today()
    try:
        item_stocks = tenant.stock_base_models.filter(item=item_id, uom=uom_id, source=warehouse_id, quantity__gte=qty, exp_date__gte=current_date).order_by('exp_date')[0]
        item_stocks.quantity = item_stocks.quantity-item['qty']
        item_stocks.save()
        
    except:
        pass
    
    return item_stocks
