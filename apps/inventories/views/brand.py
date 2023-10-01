from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.inventories.models.brand import Brand
from apps.inventories.serializers.brand import BrandSerializer
from apps.share.views import get_tenant_user


class BrandView(generics.ListCreateAPIView):
    queryset = Brand
    serializer_class = BrandSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            brand = tenant.brand_base_models.all().order_by("-created_at")
            return brand

        else:
            print("Tenant id not found")

    def perform_create(self, serializer):
        user_tenant = get_tenant_user(self)

        if user_tenant is not None:
            serializer.validated_data["tenant_id"] = user_tenant.tenant.id
            return super().perform_create(serializer)

        else:
            print("Tenant id not found")


class BrandDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Brand
    serializer_class = BrandSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_object(self):
        brand_id = self.kwargs.get("pk")
        brand = self.queryset.objects.get(id=brand_id)
        return brand

    def perform_update(self, serializer):
        user_tenant = get_tenant_user(self)

        brand_user_tenant = self.get_object().tenant

        if user_tenant != None:
            if brand_user_tenant == user_tenant.tenant:
                serializer.validated_data["tenant_id"] = user_tenant.tenant.id
                return super().perform_update(serializer)
            else:
                print("You cant't upadate! Not same tenant.")
        else:
            print("Tenant id not found!")

    def perform_destroy(self, instance):
        user_tenant = get_tenant_user(self)
        brand_user_tenant = self.get_object().tenant
        if user_tenant.tenant == brand_user_tenant:
            return super().perform_destroy(instance)
        else:
            print("You can't delete! Not same tenant.")
