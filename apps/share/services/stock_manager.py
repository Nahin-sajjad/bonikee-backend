from apps.inventories.models.stock import Stock
from apps.inventories.models.uom import UOM
from apps.share.views import get_tenant_user


class StockManager:
    def __init__(self, stock_id: str) -> str:
        self.stock_id = stock_id

    def adjust(self, new_quantity_on_hand):
        obj = {"quantity": new_quantity_on_hand}
        return obj

    def stock_transfer(self, tenant, stock_identity, quantity, source_id, item_id, per_pack_qty, lot_number, exp_date, uom_id, non_pack_qty, last_recvd_date):
        obj = {
            'tenant': tenant,
            'stock_identity': stock_identity,
            'quantity': quantity,
            'source_id':  source_id,
            'item_id': item_id,
            'lot_number': lot_number,
            'per_pack_qty': per_pack_qty,
            'exp_date': exp_date,
            'uom_id': uom_id,
            'non_pack_qty': non_pack_qty,
            'last_recvd_date': last_recvd_date,
        }
        return obj

    def stock_create_or_update(self, obj):
        stock, created = Stock.objects.update_or_create(
            id=self.stock_id, defaults=obj)

        if created:
            print("New Stock Created")

        return stock
