from django.db.models import Q

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.inventories.models.stock import Stock
from apps.inventories.models.warehouse import Warehouse
from apps.inventories.serializers.stock import StockSerializer

from apps.share.views import get_tenant_user


class StockView(generics.ListCreateAPIView):
    """
    View for listing and creating Stock objects.

    Attributes:
        queryset (QuerySet): The queryset for retrieving Stock objects.
        serializer_class (Serializer): The serializer class for Stock objects.
    """

    queryset = Stock
    serializer_class = StockSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        """
        Get a queryset of Stock objects for the current tenant.

        Returns:
            QuerySet: The queryset of Stock objects.
        """
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            stocks = tenant.stock_base_models.all()
            return stocks
        else:
            raise Exception("Permission denied!")


class WarehouseStockView(generics.ListCreateAPIView):
    """
    View for listing and creating Stock objects for a specific Warehouse.

    Attributes:
        queryset (QuerySet): The queryset for retrieving Stock objects.
        serializer_class (Serializer): The serializer class for Stock objects.
    """

    queryset = Stock
    serializer_class = StockSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_warehouse_object(self, warehouse_id, tenant):
        """
        Get the Warehouse object based on the provided ID.

        Args:
            warehouse_id (int): The ID of the Warehouse.
            tenant (Tenant): The current tenant.

        Returns:
            Warehouse: The Warehouse object.
        """
        if warehouse_id == 0:
            warehouse = tenant.warehouse_base_models.all().get(is_primary=True)
        else:
            warehouse = Warehouse.objects.get(id=warehouse_id)

        return warehouse

    def get_queryset(self):
        """
        Get a queryset of Stock objects for the current tenant and a specific Warehouse.

        Returns:
            QuerySet: The queryset of Stock objects.
        """
        user_tenant = get_tenant_user(self)
        tenant = user_tenant.tenant
        warehouse_id = self.kwargs.get("pk")

        warehouse = self.get_warehouse_object(warehouse_id, tenant)

        if warehouse_id == 0:
            stocks = (
                tenant.stock_base_models.filter(
                    Q(quantity__gt=0) | Q(non_pack_qty__gt=0)
                )
                .select_related("item")
                .select_related("uom")
                .order_by("-created_at")
            )
            return stocks
        else:
            if user_tenant is not None:
                stocks = (
                    tenant.stock_base_models.filter(
                        Q(source=warehouse, quantity__gt=0)
                        | Q(source=warehouse, non_pack_qty__gt=0)
                    )
                    .select_related("item")
                    .select_related("uom")
                    .order_by("-created_at")
                )
                return stocks
            else:
                print("Tenant id not found")

    def perform_create(self, serializer):
        """
        Perform creation of a new Stock object.

        Args:
            serializer (Serializer): The Stock serializer.

        Returns:
            HttpResponse: The HTTP response.
        """
        user_tenant = get_tenant_user(self)

        if user_tenant is not None:
            serializer.validated_data["tenant_id"] = user_tenant.tenant.id
            return super().perform_create(serializer)
        else:
            print("Tenant id not found")
