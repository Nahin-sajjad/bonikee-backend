from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.customers.models.customer import Customer
from apps.customers.serializers.customer import CustomerSerializer
from apps.share.views import get_tenant_user


class CustomerView(generics.ListCreateAPIView):
    queryset = Customer
    serializer_class = CustomerSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            customer = tenant.customer_base_models.all().order_by("-created_at")
            return customer

        else:
            print("Tenant id not found")

    def perform_create(self, serializer):
        user_tenant = get_tenant_user(self)

        if user_tenant is not None:
            serializer.validated_data["tenant_id"] = user_tenant.tenant.id
            return super().perform_create(serializer)

        else:
            print("Tenant id not found")


class CustomerDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer
    serializer_class = CustomerSerializer

    def get_object(self):
        customer_id = self.kwargs.get("pk")
        customer = self.queryset.objects.get(id=customer_id)
        return customer

    def perform_update(self, serializer):
        user_tenant = get_tenant_user(self)

        customer_user_tenant = self.get_object().tenant

        if user_tenant != None:
            if customer_user_tenant == user_tenant.tenant:
                serializer.validated_data["tenant_id"] = user_tenant.tenant.id
                return super().perform_update(serializer)
            else:
                print("You cant't upadate! Not same tenant.")
        else:
            print("Tenant id not found!")

    def perform_destroy(self, instance):
        user_tenant = get_tenant_user(self)
        customer_user_tenant = self.get_object().tenant
        if user_tenant.tenant == customer_user_tenant:
            return super().perform_destroy(instance)
        else:
            print("You can't delete! Not same tenant.")
