from rest_framework import serializers
from apps.finance.models.transaction import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display", read_only=True)
    tran_type = serializers.CharField(
        source="get_tran_type_display", read_only=True)
    tran_group = serializers.CharField(
        source="get_tran_group_display", read_only=True)
    tran_head = serializers.CharField(
        source="get_tran_head_display", read_only=True)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "tran_number",
            "tran_date",
            "amount",
            "tran_type",
            "tran_group",
            "tran_head",
            "status",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["tran_date"] = instance.tran_date.strftime("%b %d, %Y")
        return representation
