from rest_framework import serializers

from apps.finance.models.inc_exp import IncExp
from apps.finance.models.inc_exp_type import IncExpType


class IncExpSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncExp
        fields = ['id', 'num', 'type', 'source_type', 'dt', 'amt',
                  'ref_num', 'pay_method', 'note', 'status']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        inc_exp_type = IncExpType.objects.get(code=instance.type)
        representation['payment_method_name'] = "Cash" if instance.pay_method == "1" else "Bank"
        representation['type_name'] = inc_exp_type.type
        return representation
