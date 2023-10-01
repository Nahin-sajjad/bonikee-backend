from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.inventories.models.uom import UOM
from apps.inventories.serializers.uom import UOMSerializer

from apps.share.views import get_tenant_user


class UomView(generics.ListCreateAPIView):
    queryset = UOM
    serializer_class = UOMSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    # def get(self, request, *args, **kwargs):
    #     return super().get(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     return super().post(request, *args, **kwargs)

    def get_queryset(self):
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            uom = tenant.uom_base_models.all().order_by("-created_at")
            return uom
        else:
            print("Tenant id not found")

    def perform_create(self, serializer):
        user_tenant = get_tenant_user(self)

        if user_tenant is not None:
            serializer.validated_data["tenant_id"] = user_tenant.tenant.id
            return super().perform_create(serializer)

        else:
            print("Tenant id not found")


class UomDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UOM
    serializer_class = UOMSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    # def get(self, request, *args, **kwargs):
    #     return super().get(request, *args, **kwargs)

    # def put(self, request, *args, **kwargs):
    #     return super().put(request, *args, **kwargs)

    # def delete(self, request, *args, **kwargs):
    #     return super().delete(request, *args, **kwargs)

    def get_object(self):
        uom_id = self.kwargs.get("pk")
        uom = self.queryset.objects.get(id=uom_id)
        return uom

    def perform_update(self, serializer):
        user_tenant = get_tenant_user(self)

        uom_user_tenant = self.get_object().tenant

        if user_tenant != None:
            if uom_user_tenant == user_tenant.tenant:
                serializer.validated_data["tenant_id"] = user_tenant.tenant.id
                return super().perform_update(serializer)
            else:
                print("You cant't upadate! Not same tenant.")
        else:
            print("Tenant id not found!")

    def perform_destroy(self, instance):
        user_tenant = get_tenant_user(self)
        uom_user_tenant = self.get_object().tenant
        if user_tenant.tenant == uom_user_tenant:
            return super().perform_destroy(instance)
        else:
            print("You can't delete! Not same tenant.")
