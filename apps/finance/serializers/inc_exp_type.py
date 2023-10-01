from rest_framework import serializers

from apps.finance.models.inc_exp_type import IncExpType


class IncExpTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncExpType
        fields = ['id', 'type', 'code']
