from django.db import transaction

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.hr.models.advance import Advance
from apps.hr.serializers.advance import AdvanceSerializer

from apps.share.views import get_tenant_user, generate_advance_number
from apps.share.services.transaction_manager import TransactionManager


class AdvanceView(generics.ListCreateAPIView):
    """
    API view for retrieving and creating advance records.

    This view allows users to retrieve a list of advance records and create new advance records.

    Attributes:
        queryset (QuerySet): The queryset to retrieve advance records for the current tenant.
        serializer_class (AdvanceSerializer): The serializer class for the Advance model.
    """

    queryset = Advance
    serializer_class = AdvanceSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        """
        Retrieve a list of advance records for the current tenant.

        Returns:
            QuerySet: A queryset of advance records ordered by creation date.
        """
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            advance = tenant.advance_base_models.all().order_by("-created_at")
            return advance
        else:
            print("Tenant id not found")

    def create(self, request, *args, **kwargs):
        """
        Create a new advance record and update the employee's advance due.

        Args:
            request (Request): The HTTP request object.
            *args: Variable-length argument list.
            **kwargs: Keyword arguments.

        Returns:
            Response: The HTTP response indicating success or failure.
        """
        tenant = get_tenant_user(self).tenant
        employee_id = request.data.get("employee")
        employee = tenant.employee_base_models.get(id=employee_id)
        adv_number = generate_advance_number(request.data.get("date"))

        with transaction.atomic():
            try:
                # Update the employee's advance due
                employee.advance_due += int(request.data.get("advance"))
                employee.save()

                try:
                    # Get the current transaction amount for the advance number
                    tran_amount = tenant.transaction_base_models.get(
                        tran_number=adv_number
                    ).amount
                except:
                    tran_amount = 0

                # Create or update the transaction record
                tran_amount += int(request.data.get("advance"))
                transaction_manage = TransactionManager(
                    tenant=tenant, tran_number=adv_number
                )
                transaction_manage.transaction_create_or_update(
                    tran_group=103, amount=tran_amount, tran_type=1014, tran_head=7
                )

                # Serialize and save the advance record
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    serializer.save(tenant=tenant)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdvanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting individual advance records.

    This view allows users to retrieve, update, and delete specific advance records.

    Attributes:
        queryset (QuerySet): The queryset to retrieve advance records for the current tenant.
        serializer_class (AdvanceSerializer): The serializer class for the Advance model.
    """

    queryset = Advance
    serializer_class = AdvanceSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def update(self, request, *args, **kwargs):
        """
        Update an existing advance record and related transactions.

        Args:
            request (Request): The HTTP request object.
            *args: Variable-length argument list.
            **kwargs: Keyword arguments.

        Returns:
            Response: The HTTP response indicating success or failure.
        """
        tenant = get_tenant_user(self).tenant
        employee_id = request.data.get("employee")
        employee = tenant.employee_base_models.get(id=employee_id)
        advance_obj = tenant.advance_base_models.get(id=request.data.get("id"))
        adv_number = generate_advance_number(request.data.get("date"))

        with transaction.atomic():
            try:
                employee.advance_due += int(request.data.get("updateAdvance"))
                employee.save()

                try:
                    # Get the current transaction amount for the advance number
                    tran_amount = tenant.transaction_base_models.get(
                        tran_number=adv_number
                    ).amount
                except:
                    tran_amount = 0

                # Create or update the transaction record
                tran_amount += int(request.data.get("updateAdvance"))
                transaction_manage = TransactionManager(
                    tenant=tenant, tran_number=adv_number
                )
                transaction_manage.transaction_create_or_update(
                    tran_group=103, amount=tran_amount, tran_type=1014, tran_head=7
                )

                # Serialize and save the updated advance record
                serializer = self.get_serializer(advance_obj, data=request.data)
                if serializer.is_valid():
                    serializer.save(tenant=tenant)
                    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

                else:
                    print(serializer.errors)
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """
        Delete an existing advance record and update the employee's advance due.

        Args:
            request (Request): The HTTP request object.
            *args: Variable-length argument list.
            **kwargs: Keyword arguments.

        Returns:
            Response: The HTTP response indicating success or failure.
        """
        tenant = get_tenant_user(self).tenant
        pk = kwargs.get("pk")
        advance_obj = tenant.advance_base_models.get(id=pk)
        employee = tenant.employee_base_models.get(id=advance_obj.employee_id)

        with transaction.atomic():
            try:
                # Reduce the employee's advance due
                employee.advance_due -= advance_obj.advance
                employee.save()

                # Delete the advance record
                advance_obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
