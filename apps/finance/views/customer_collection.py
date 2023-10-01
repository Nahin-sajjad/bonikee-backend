from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.finance.models.customer_collection import CustomerCollection
from apps.finance.serializers.customer_collection import CustomerCollectionSerializer

from apps.share.views import get_tenant_user
from apps.share.views import number_generate
from apps.share.services.transaction_manager import TransactionManager

from datetime import datetime


class CustomerCollectionView(generics.ListCreateAPIView):
    queryset = CustomerCollection
    serializer_class = CustomerCollectionSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            customer_collection = tenant.customercollection_base_models.all().order_by(
                "-created_at"
            )
            return customer_collection

        else:
            print("Tenant id not found")

    def create(self, request, *args, **kwargs):
        user_tenant = get_tenant_user(self).tenant
        data = request.data
        if user_tenant is not None:
            try:
                last_rec = user_tenant.customercollection_base_models.last()
                previous_number = last_rec.collection_num
            except:
                previous_number = f"COL-{datetime.now().year}-{0}"

            collection_number = number_generate(previous_number)
            data["collection_num"] = collection_number

            serializer = self.get_serializer(data=data)

            if serializer.is_valid():
                try:
                    collection = serializer.save(tenant=user_tenant)
                    transaction_manage = TransactionManager(
                        tenant=user_tenant, tran_number=data["collection_num"]
                    )
                    transaction_manage.transaction_create_or_update(
                        tran_group=102,
                        amount=data["amount"],
                        tran_type=1008,
                        tran_head=3,
                    )

                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response(
                        str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                print(serializer.errors)
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            print("Tenant id not found")


class CustomerCollectionDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomerCollection
    serializer_class = CustomerCollectionSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_object(self):
        customer_collection_id = self.kwargs.get("pk")
        customer_collection = self.queryset.objects.get(id=customer_collection_id)
        return customer_collection

    def perform_update(self, serializer):
        user_tenant = get_tenant_user(self)

        customer_collection_user_tenant = self.get_object().tenant

        if user_tenant != None:
            if customer_collection_user_tenant == user_tenant.tenant:
                serializer.validated_data["tenant_id"] = user_tenant.tenant.id
                return super().perform_update(serializer)
            else:
                print("You cant't upadate! Not same tenant.")
        else:
            print("Tenant id not found!")

    def perform_destroy(self, instance):
        user_tenant = get_tenant_user(self)
        customer_collection_user_tenant = self.get_object().tenant
        if user_tenant.tenant == customer_collection_user_tenant:
            return super().perform_destroy(instance)
        else:
            print("You can't delete! Not same tenant.")
