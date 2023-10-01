from django.db import transaction

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.finance.models.customer_receivable import CustomerReceivable
from apps.finance.serializers.customer_receivable import CustomerReceivableSerializer

from apps.share.views import get_tenant_user
from apps.share.views import number_generate
from apps.share.services.transaction_manager import TransactionManager

from datetime import datetime


class CustomerReceivableView(generics.ListCreateAPIView):
    queryset = CustomerReceivable
    serializer_class = CustomerReceivableSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            customer_receivable = tenant.customerreceivable_base_models.all().order_by(
                "-created_at"
            )
            return customer_receivable

        else:
            print("Tenant id not found")

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            user_tenant = get_tenant_user(self).tenant
            data = request.data
            if user_tenant is not None:
                try:
                    last_rec = user_tenant.customerreceivable_base_models.last()
                    previous_number = last_rec.receivable_num
                except:
                    previous_number = f"REC-{datetime.now().year}-{0}"

                receivable_number = number_generate(previous_number)
                data["receivable_num"] = receivable_number

                serializer = self.get_serializer(data=data)

                if serializer.is_valid():
                    try:
                        rcvble = serializer.save(tenant=user_tenant)
                        transaction_manage = TransactionManager(
                            tenant=user_tenant, tran_number=data["receivable_num"]
                        )
                        transaction_manage.transaction_create_or_update(
                            tran_group=101,
                            amount=data["amount"],
                            tran_type=1007,
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


class CustomerReceivableDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomerReceivable
    serializer_class = CustomerReceivableSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_object(self):
        customer_receivable_id = self.kwargs.get("pk")
        customer_receivable = self.queryset.objects.get(id=customer_receivable_id)
        return customer_receivable

    def perform_update(self, serializer):
        user_tenant = get_tenant_user(self)

        customer_receivable_user_tenant = self.get_object().tenant

        if user_tenant != None:
            if customer_receivable_user_tenant == user_tenant.tenant:
                serializer.validated_data["tenant_id"] = user_tenant.tenant.id
                return super().perform_update(serializer)
            else:
                print("You cant't upadate! Not same tenant.")
        else:
            print("Tenant id not found!")

    def perform_destroy(self, instance):
        user_tenant = get_tenant_user(self)
        customer_receivable_user_tenant = self.get_object().tenant
        if user_tenant.tenant == customer_receivable_user_tenant:
            return super().perform_destroy(instance)
        else:
            print("You can't delete! Not same tenant.")
