from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from apps.share.services.stock_manager import StockManager

from apps.inventories.models.stock_price import StockPrice


def manage_stock(stock_id):
    stock_manager = StockManager(stock_id)
    return stock_manager


def stock_exists_obj(tenant, obj, identity):
    try:
        non_pack_qty = obj['non_pack_qty']
    except:
        non_pack_qty = 0

    try:
        des_stock = tenant.stock_base_models.get(
            source_id=obj['recvd_stock'], stock_identity=identity, item=obj['item'])
        des_stock.quantity += obj['recvd_qty']
        # des_stock.non_pack_qty += non_pack_qty
        des_stock.last_recvd_date = obj['recvd_date']
        des_stock.save()
        stock_price = tenant.stockprice_base_models.get(
            item=des_stock.item)
        des_stock.item_price = stock_price
        stock_price.unit_price = obj['cost_per_unit']
        stock_price.save()

    except:
        stock_manager = manage_stock(stock_id=None)
        stock_obj = stock_manager.stock_transfer(
            tenant=tenant,
            stock_identity=identity,
            quantity=obj['recvd_qty'],
            lot_number=obj['lot_number'],
            exp_date=obj['exp_date'],
            source_id=obj['recvd_stock'],
            item_id=obj['item'],
            per_pack_qty=obj['per_pack_qty'],
            uom_id=obj['uom'],
            non_pack_qty=non_pack_qty,
            last_recvd_date=obj['recvd_date'],
        )
        des_stock = stock_manager.stock_create_or_update(stock_obj)
        stock_price, _ = StockPrice.objects.update_or_create(item=des_stock.item,
                                                             defaults={"tenant": tenant, "item": des_stock.item,  "sales_price": obj['cost_per_unit']})
        des_stock.item_price = stock_price
        des_stock.save()

    return des_stock


def stock_exists(tenant, recvd_stock_id, production_identity, item_id, uom_id, recvd_qty, lot_number, exp_date, per_pack_qty, non_pack_qty, last_unit_price, date):
    try:
        with transaction.atomic():
            try:
                des_stock = tenant.stock_base_models.get(
                    source_id=recvd_stock_id, stock_identity=production_identity, item_id=item_id)
                des_stock.quantity += recvd_qty
                des_stock.non_pack_qty += non_pack_qty
                if date != 0:
                    des_stock.last_recvd_date = date

                des_stock.save()
                stock_price = tenant.stockprice_base_models.get(
                    item_id=des_stock.item.id)
                if last_unit_price > 0:
                    stock_price.unit_price = last_unit_price
                stock_price.save()
            except Exception as e:
                transaction.set_rollback(True)  # Rollback the transaction
                raise

    except ObjectDoesNotExist:
        with transaction.atomic():
            try:
                stock_manager = manage_stock(None)
                obj = stock_manager.stock_transfer(
                    tenant=tenant,
                    stock_identity=production_identity,
                    quantity=recvd_qty,
                    lot_number=lot_number,
                    exp_date=exp_date,
                    source_id=recvd_stock_id,
                    item_id=item_id,
                    per_pack_qty=per_pack_qty,
                    uom_id=uom_id,
                    non_pack_qty=non_pack_qty,
                    last_recvd_date=date,
                )
                des_stock = stock_manager.stock_create_or_update(obj)
                stock_price = StockPrice.objects.create(
                    tenant=tenant, item=des_stock.item, unit_price=last_unit_price, sales_price=last_unit_price)

            except Exception as e:
                transaction.set_rollback(True)  # Rollback the transaction
                raise

    return des_stock
