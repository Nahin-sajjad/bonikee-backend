from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.inventories.models.warehouse import Warehouse
from apps.inventories.serializers.warehouse import WarehouseSerializer

from apps.share.views import get_tenant_user


class WarehouseView(generics.ListCreateAPIView):
    queryset = Warehouse
    serializer_class = WarehouseSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            item = tenant.warehouse_base_models.all()
            return item
        else:
            # print("Tenant id not found")
            raise Exception("Tenant id not found")

    def perform_create(self, serializer):
        # set your logic
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            serializer.validated_data["tenant_id"] = user_tenant.tenant.id
            tenant_primary_warehouses = tenant.warehouse_base_models.all().filter(
                is_primary=True
            )
            is_primary = self.request.data.get("is_primary")
            if is_primary:
                # serializer.validated_data["is_primary"] = True
                tenant_primary_warehouses.update(is_primary=False)
                # Warehouse.objects.bulk_update(tenant_primary_warehouses, ['is_primary'])

        return super().perform_create(serializer)


class WarehouseDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Warehouse
    serializer_class = WarehouseSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_object(self):
        warehouse_id = self.kwargs.get("pk")
        warehouse = self.queryset.objects.get(id=warehouse_id)
        return warehouse

    def perform_update(self, serializer):
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            tenant_primary_warehouses = tenant.warehouse_base_models.all().filter(
                is_primary=True
            )
            is_primary = self.request.data.get("is_primary")

            # print("self.request.data: ",self.request.data)
            warehouse_tenant = self.get_object().tenant
            if tenant == warehouse_tenant:
                if is_primary:
                    serializer.validated_data["is_primary"] = True
                    tenant_primary_warehouses.update(is_primary=False)
                    # Warehouse.objects.bulk_update(tenant_primary_warehouses, ['is_primary'])

                return super().perform_update(serializer)
        else:
            # print('Tenant id not found')
            raise Exception("Tenant id not found")

    def perform_destroy(self, instance):
        user_tenant = get_tenant_user(self)
        warehouse_user_tenant = self.get_object().tenant
        if user_tenant.tenant == warehouse_user_tenant:
            return super().perform_destroy(instance)
        else:
            # print("can not delete not same tenant")
            raise Exception("Can not delete not same tenant")
