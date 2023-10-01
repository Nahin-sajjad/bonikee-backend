from django.db import transaction

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.sales.models.invoice import Invoice
from apps.sales.serializers.invoice import (
    InvoiceSerializer,
    InvoiceLineItemSerializer,
)

from apps.share.views import number_generate
from apps.share.services.transaction_manager import TransactionManager
from apps.share.views import get_tenant_user

from datetime import date, datetime


class InvoiceView(generics.ListCreateAPIView):
    queryset = Invoice
    serializer_class = InvoiceSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            invoice = tenant.invoice_base_models.all().order_by("-created_at")
            return invoice

        else:
            print("Tenant id not found")

    def create(self, request, *args, **kwargs):
        tenant = get_tenant_user(self).tenant
        data = request.data

        if tenant is not None:
            try:
                last_rec = tenant.invoice_base_models.last()
                previous_number = last_rec.inv_num
            except:
                previous_number = f"INV-{datetime.now().year}-{0}"

            inv_num = number_generate(previous_number)

            data["inv_num"] = inv_num
            inv_line_items = request.data["inv_line_items"]

            serializer = self.get_serializer(data=data)

            if serializer.is_valid():
                with transaction.atomic():
                    try:
                        ## Creating Invoice
                        inv = serializer.save(tenant=tenant)
                        warehouse_id = data["warehouse"]

                        for items in inv_line_items:
                            items["inv"] = inv.id
                            item_id = items["item_id"]
                            uom_id = items["unit"]
                            qty = items["qty"]

                            current_date = date.today()
                            item_stocks = (
                                tenant.stock_base_models.filter(
                                    item=item_id,
                                    uom=uom_id,
                                    source=warehouse_id,
                                    quantity__gte=qty,
                                    exp_date__gte=current_date,
                                )
                                .order_by("exp_date")
                                .first()
                            )
                            print(item_stocks)

                            if item_stocks:
                                item_stocks.quantity = item_stocks.quantity - float(qty)
                                item_stocks.save()
                            else:
                                return Response(
                                    "Item Stock Not Found",
                                    status=status.HTTP_404_NOT_FOUND,
                                )

                        inv_line_item_serializer = InvoiceLineItemSerializer(
                            data=inv_line_items, many=True
                        )

                        if inv_line_item_serializer.is_valid():
                            inv_line_item_serializer.save(tenant=tenant)
                        else:
                            return Response(
                                inv_line_item_serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST,
                            )

                        # income_data = {
                        #     "inc_type_cd": "Sale",
                        #     "amt": inv.paid_amount,
                        #     "pay_method": data["payment_method"],
                        #     "ref": data["inv_num"],
                        #     "paid_by": data["cust"],
                        # }
                        # income_serializer = IncomeSerializer(data=income_data)

                        # if income_serializer.is_valid():
                        #     income_serializer.save(tenant=tenant)
                        # else:
                        #     return Response(income_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                        transaction_manage = TransactionManager(
                            tenant=tenant, tran_number=inv.inv_num
                        )
                        transaction_manage.transaction_create_or_update(
                            tran_group=102,
                            amount=inv.paid_amount,
                            tran_type=1002,
                            tran_head=1,
                        )

                        if inv.paid_amount != 0 and inv.total_amount > inv.paid_amount:
                            inv.status = 2
                        elif inv.paid_amount == inv.total_amount:
                            inv.status = 3

                        inv.save()

                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    except Exception as e:
                        transaction.set_rollback(True)  # Rollback the transaction
                        return Response(
                            str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("Tenant not found.")


class InvoiceDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Invoice
    serializer_class = InvoiceSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_object(self):
        invoice_id = self.kwargs.get("pk")
        invoice = self.queryset.objects.get(id=invoice_id)
        return invoice

    def perform_update(self, serializer):
        user_tenant = get_tenant_user(self)

        invoice_user_tenant = self.get_object().tenant

        if user_tenant != None:
            if invoice_user_tenant == user_tenant.tenant:
                serializer.validated_data["tenant_id"] = user_tenant.tenant.id
                tenant = user_tenant.tenant
                # income_rec = tenant.incexp_base_models.get(
                #     ref=serializer.validated_data["inv_num"]
                # )
                # income_rec.amt = serializer.validated_data["paid_amount"]
                # income_rec.save()

                if (
                    serializer.validated_data["paid_amount"]
                    == serializer.validated_data["total_amount"]
                ):
                    serializer.validated_data["status"] = 3
                elif (
                    serializer.validated_data["paid_amount"]
                    < serializer.validated_data["total_amount"]
                    and serializer.validated_data["paid_amount"] > 0
                ):
                    serializer.validated_data["status"] = 2

                return super().perform_update(serializer)
            else:
                print("You cant't upadate! Not same tenant.")
        else:
            print("Tenant id not found!")

    def perform_destroy(self, instance):
        user_tenant = get_tenant_user(self)
        invoice_user_tenant = self.get_object().tenant
        if user_tenant.tenant == invoice_user_tenant:
            return super().perform_destroy(instance)
        else:
            print("You can't delete! Not same tenant.")
