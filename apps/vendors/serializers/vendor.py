from rest_framework import serializers
from apps.vendors.models.vendor import Vendor

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ('address', 'company', 'email', 'phone', 'vendor_name', 'id', 'created_at', 'edited_at')

    def to_representation(self, instance):
        # Get all vendor_pays and vendor_payables related to the vendor
        vendor_pays = instance.vendor_pays.all()
        vendor_payables = instance.vendor_payables.all()

        # Calculate the total amount for vendor_pays
        total_vendor_pays = sum(pay.amt for pay in vendor_pays)

        # Calculate the total amount for vendor_payables
        total_vendor_payables = sum(payable.amt for payable in vendor_payables)

        # Calculate the due amount by subtracting payments from payables
        due_amount = total_vendor_payables - total_vendor_pays

        # Create the serialized representation
        representation = super().to_representation(instance)
        representation['total_payable_amount'] = due_amount if due_amount is not None else 0

        return representation
