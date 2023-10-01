from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.sales.models.sale_return import SaleReturn, SaleReturnLineItem
from apps.sales.serializers.sale_return import (
    SaleReturnSerializer,
    SaleReturnLineItemSerializer,
)

from apps.inventories.models.stock import Stock

from apps.share.views import get_tenant_user
from apps.share.services.transaction_manager import TransactionManager

from django.db import transaction


class SaleReturnView(generics.ListCreateAPIView):
    """
    API view for listing and creating sale returns.

    Attributes:
        queryset (QuerySet): The queryset for retrieving sale returns.
        serializer_class (Serializer): The serializer class for sale returns.
    """

    queryset = SaleReturn
    serializer_class = SaleReturnSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        """
        Get the queryset of sale returns for the current tenant.

        Returns:
            QuerySet: The queryset of sale returns.
        """
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            sale_return_list = tenant.salereturn_base_models.all().order_by("-id")
            return sale_return_list
        else:
            print("Tenant id not found")

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create a new sale return and associated line items.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: The HTTP response.
        """
        line_items = request.data["lineItems"]
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_tenant = get_tenant_user(self)
            tenant = user_tenant.tenant
            sale_return = serializer.save(
                tenant=tenant, inv_id=request.data.get("invoice", None)
            )
            if sale_return:
                for line_item in line_items:
                    try:
                        ret_qty = int(line_item["ret_qty"])
                    except:
                        ret_qty = 0

                    line_item_serializer = SaleReturnLineItemSerializer(data=line_item)

                    if line_item_serializer.is_valid():
                        line_item_serializer.save(
                            tenant=tenant,
                            sale_ret=sale_return,
                            inv_item_id=line_item["id"],
                        )

                        stock_id = line_item["item"]
                        stock = Stock.objects.get(id=stock_id)
                        stock.quantity = stock.quantity + ret_qty
                        stock.save()
                transaction_manager = TransactionManager(
                    tenant=tenant, tran_number=sale_return.inv.inv_num
                )

                transaction_manager.transaction_create_or_update(
                    tran_group=2,
                    amount=sale_return.ret_amount,
                    tran_type=1003,
                    tran_head=1,
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SaleReturnDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a sale return.

    Attributes:
        queryset (QuerySet): The queryset for retrieving sale returns.
        serializer_class (Serializer): The serializer class for sale returns.
    """

    queryset = SaleReturn
    serializer_class = SaleReturnSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_object(self):
        sale_return_id = self.kwargs.get("pk")
        sale_return = self.queryset.objects.get(id=sale_return_id)
        return sale_return

    def update(self, request, *args, **kwargs):
        """
        Handle PUT requests to update a sale return and associated line items.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: The HTTP response.
        """
        sale_return = self.get_object()
        line_items = request.data["lineItems"]
        serializer = self.serializer_class(sale_return, data=request.data)
        if serializer.is_valid():
            user_tenant = get_tenant_user(self)
            tenant = user_tenant.tenant
            sale_return = serializer.save(
                tenant=tenant, inv_id=request.data.get("invoice", None)
            )
            if sale_return:
                for line_item in line_items:
                    try:
                        ret_qty = int(line_item["ret_qty"])
                    except:
                        ret_qty = 0

                    line_item_obj = SaleReturnLineItem.objects.get(id=line_item["id"])
                    line_item_serializer = SaleReturnLineItemSerializer(
                        line_item_obj, data=line_item
                    )

                    if line_item_serializer.is_valid():
                        line_item_serializer.save(
                            tenant=tenant,
                            sale_ret=sale_return,
                            inv_item_id=line_item["inv_item"],
                        )
                        stock_id = line_item["item"]
                        stock = Stock.objects.get(id=stock_id)
                        stock.quantity = stock.quantity + ret_qty
                        stock.save()
                transaction_manager = TransactionManager(
                    tenant=tenant, tran_number=sale_return.inv.inv_num
                )

                transaction_manager.transaction_obj(
                    tran_group=103,
                    amount=sale_return.ret_amount,
                    tran_type=1003,
                    tran_head=1,
                )
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Handle DELETE requests to delete a sale return.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: The HTTP response.
        """
        return super().destroy(request, *args, **kwargs)
