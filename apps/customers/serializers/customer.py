from rest_framework import serializers

from apps.customers.models.customer import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = (
            "id",
            "customer_name",
            "phone",
            "email",
            "address",
        )

    def to_representation(self, instance):
        # Get all customer_collections and customer_receivables related to the customer
        customer_collections = instance.customer_collections.all()
        customer_receivables = instance.customer_receivables.all()

        # Calculate the total amount for customer_collections
        total_customer_collections = sum(
            collection.amount for collection in customer_collections
        )

        # Calculate the total amount for customer_receivables
        total_customer_receivables = sum(
            receivable.amount for receivable in customer_receivables
        )

        # Calculate the due amount by subtracting payments from receivables
        due_amount = total_customer_receivables - total_customer_collections

        # Create the serialized representation
        representation = super().to_representation(instance)
        representation["total_receivable_amount"] = (
            due_amount if due_amount is not None else 0
        )

        return representation
