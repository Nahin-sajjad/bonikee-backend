from django.db import transaction

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.inventories.models.transfer import Transfer
from apps.inventories.serializers.transfer import (
    TransferSerializer,
    TransferItemSerializer,
)

from apps.share.views import get_tenant_user
from apps.share.services.stock_common import stock_exists_obj
from apps.share.services.stock_manager import StockManager
from apps.share.services.tenant_error_logger import TenantLogger


class TransferView(generics.ListCreateAPIView):
    queryset = Transfer
    serializer_class = TransferSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def manage_stock(self, stock_id):
        """
        Create and return a StockManager instance for the given stock ID.

        Args:
            stock_id (int): The ID of the stock to manage.

        Returns:
            StockManager: A StockManager instance for the specified stock.
        """
        stock_manager = StockManager(stock_id)
        return stock_manager

    def stock_obj(self, stock):
        """
        Create a dictionary representing a stock object based on the provided data.

        Args:
            stock (dict): The stock data to create the object from.

        Returns:
            dict: A dictionary representing a stock object.
        """
        obj = {
            "recvd_stock": stock["source"],
            "item": stock["item"],
            "recvd_qty": stock["quantity"],
            "recvd_date": stock["date"],
            "cost_per_unit": stock["price"],
            "lot_number": stock["lot_number"],
            "exp_date": stock["exp_date"],
            "per_pack_qty": stock["per_pack_qty"],
            "uom": stock["uom"],
            "non_pack_qty": stock["non_pack_qty"],
        }
        return obj

    def get_queryset(self):
        """
        Get the queryset of Transfer objects for the current tenant.

        Returns:
            QuerySet: The queryset of Transfer objects ordered by creation date.
        """
        return (
            get_tenant_user(self)
            .tenant.transfer_base_models.all()
            .order_by("-created_at")
        )

    def create(self, request):
        """
        Create a new Transfer record.

        This method handles the creation of a new Transfer record along with its related TransferItem records.
        It also manages stock objects associated with the Transfer.

        Args:
            request (Request): The HTTP POST request containing Transfer and TransferItem data.

        Returns:
            Response: HTTP response indicating the success or failure of the creation operation.
        """
        tenant_logger = TenantLogger(request)
        tenant = get_tenant_user(self).tenant
        last_transfer = (
            tenant.transfer_base_models.last().transfer_no
            if tenant.transfer_base_models.exists()
            else 0
        )
        transfer_no = last_transfer + 1
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                # Create the Transfer record
                transfer = serializer.save(
                    tenant=tenant,
                    transfer_no=transfer_no,
                    from_stk_id=request.data["from_stk"],
                    to_stk_id=request.data["to_stk"],
                )

                # Create or update TransferItem records
                for transfer_item in request.data["transfers"]:
                    item_serializer = TransferItemSerializer(data=transfer_item)
                    if item_serializer.is_valid():
                        item_serializer.save(
                            tenant=tenant,
                            transfer=transfer,
                            des_stock_identity=transfer_item["des_stock_identity"],
                        )
                    else:
                        tenant_logger.error(item_serializer.errors)
                        return Response(
                            item_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                # Create or update primary_stock objects
                primary_stock = request.data["primary_stock"]
                for stock in primary_stock:
                    stock_manager = self.manage_stock(stock["id"])
                    stock_manager.stock_create_or_update(stock)

                # Create or update des_stock objects
                des_stock = request.data["des_stock"]
                for stock in des_stock:
                    stock_obj = self.stock_obj(stock=stock)
                    stock_manager = stock_exists_obj(
                        tenant, stock_obj, stock["stock_identity"]
                    )

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(e)  # Log the exception for debugging purposes
                tenant_logger.error(e)
                return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            print(serializer.errors)  # Log serializer errors for debugging purposes
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransferDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transfer
    serializer_class = TransferSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def stock_obj(self, stock, stock_manager, data):
        """
        Create a dictionary representing a stock object based on the provided data.

        Args:
            stock (dict): The stock data.
            stock_manager (StockManager): The StockManager instance.
            data (dict): The request data.

        Returns:
            dict: A dictionary representing a stock object.
        """
        obj = {
            "recvd_stock": data["to_stk"],
            "item": stock_manager.item.id,
            "recvd_qty": stock["quantity"],
            "recvd_date": stock_manager.last_recvd_date,
            "cost_per_unit": stock_manager.item_price.sales_price,
            "lot_number": stock_manager.lot_number,
            "exp_date": stock_manager.exp_date,
            "per_pack_qty": stock_manager.per_pack_qty,
            "uom": stock["uom"],
            "non_pack_qty": stock["non_pack_qty"],
        }
        return obj

    def manage_stock(self, stock_id):
        """
        Create and return a StockManager instance for the given stock ID.

        Args:
            stock_id (int): The ID of the stock to manage.

        Returns:
            StockManager: A StockManager instance for the specified stock.
        """
        stock_manager = StockManager(stock_id)
        return stock_manager

    def update(self, request, pk):
        """
        Update a Transfer record and related TransferItem records.

        Args:
            request (Request): The HTTP PUT request containing updated data.
            pk (int): The primary key of the Transfer record to update.

        Returns:
            Response: HTTP response indicating the success or failure of the update operation.
        """
        tenant = get_tenant_user(self).tenant
        transfer_obj = tenant.transfer_base_models.all().get(id=pk)
        transfer_item_objects = transfer_obj.transfers.all()
        serializer = self.get_serializer(transfer_obj, data=request.data)

        if serializer.is_valid():
            with transaction.atomic():
                serializer.save()
                transferred_items = request.data["transfers"]

                for transfer_item in transferred_items:
                    t_item = transfer_item_objects.get(id=transfer_item["id"])
                    item_serializer = TransferItemSerializer(t_item, data=transfer_item)

                    if item_serializer.is_valid():
                        item_serializer.save()

                        # Create or update the primary_stock objects
                        primary_stock = request.data["primary_stock"]

                        for stock in primary_stock:
                            stock_manager = self.manage_stock(stock["id"])
                            stock_manager.stock_create_or_update(stock)

                        # Create or update the des_stock objects
                        des_stock = request.data["des_stock"]

                        for stock in des_stock:
                            stock_manager = tenant.stock_base_models.get(id=stock["id"])
                            stock_manager.quantity -= int(stock["trans_qty"])
                            stock_manager.save()
                            stock_obj = self.stock_obj(
                                stock, stock_manager, request.data
                            )
                            stock_exists_obj(
                                tenant, stock_obj, stock_manager.stock_identity
                            )

                        if transfer_item["trans_qty"] == 0:
                            t_item.delete()
                    else:
                        # Rollback the transaction
                        transaction.set_rollback(True)
                        return Response(
                            item_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                        )

                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        """
        Delete a Transfer record and update related stock quantities.

        Args:
            request (Request): The HTTP DELETE request.
            pk (int): The primary key of the Transfer record to delete.

        Returns:
            Response: HTTP response indicating the success or failure of the delete operation.
        """
        tenant = get_tenant_user(self).tenant
        transfer_obj = tenant.transfer_base_models.all().get(id=pk)
        transfer_item_objects = transfer_obj.transfers.all()

        with transaction.atomic():
            try:
                for transfer_item in transfer_item_objects:
                    primary_stock = transfer_item.stock
                    des_stock = tenant.stock_base_models.get(
                        source=transfer_obj.to_stk,
                        stock_identity=primary_stock.stock_identity,
                        item_id=primary_stock.item.id,
                    )

                    # Update Primary Stock
                    if transfer_item.trans_unit == primary_stock.uom:
                        primary_stock.quantity += transfer_item.trans_qty
                    elif (
                        primary_stock.uom
                        == primary_stock.item.uom
                        == transfer_item.trans_unit
                    ):
                        primary_stock.quantity += transfer_item.trans_qty
                        primary_stock.non_pack_qty += transfer_item.trans_qty
                    else:
                        up_pack_qty = int(
                            transfer_item.trans_qty / primary_stock.per_pack_qty
                        )
                        extra_qty = int(
                            transfer_item.trans_qty
                            - (primary_stock.per_pack_qty * up_pack_qty)
                        )
                        primary_stock.quantity += up_pack_qty
                        primary_stock.non_pack_qty += extra_qty
                    primary_stock.save()

                    # Update Des Stock
                    if transfer_item.trans_unit == des_stock.uom:
                        des_stock.quantity += transfer_item.trans_qty
                    elif (
                        des_stock.uom == des_stock.item.uom == transfer_item.trans_unit
                    ):
                        des_stock.quantity += transfer_item.trans_qty
                        des_stock.non_pack_qty += transfer_item.trans_qty
                    else:
                        up_pack_qty = int(
                            transfer_item.trans_qty / des_stock.per_pack_qty
                        )
                        extra_qty = int(
                            transfer_item.trans_qty
                            - (des_stock.per_pack_qty * up_pack_qty)
                        )
                        des_stock.quantity += up_pack_qty
                        des_stock.non_pack_qty += extra_qty
                    des_stock.save()

                    transfer_item.delete()

                transfer_obj.delete()

                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                transaction.set_rollback(True)  # Rollback the transaction
                return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
