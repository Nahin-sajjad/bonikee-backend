from rest_framework import serializers
from apps.hr.models.advance import Advance


class AdvanceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Advance model.

    This serializer is used to convert Advance model instances to JSON representations and vice versa.

    Attributes:
        adv_type_label (CharField): A read-only field to display the human-readable advance type label.
        date (DateTimeField): A field to format the date as 'yyyy-MM-dd'.
    """

    adv_type_label = serializers.CharField(
        source="get_adv_type_display", read_only=True, required=False
    )
    date = serializers.DateTimeField(
        format="%Y-%m-%d"
    )  # Format the date field as 'yyyy-MM-dd'

    class Meta:
        model = Advance
        fields = ("id", "date", "adv_type", "advance", "adv_type_label", "employee")

    def to_representation(self, instance):
        """
        Convert Advance model instance to JSON representation with additional computed fields.

        Args:
            instance (Advance): The Advance model instance.

        Returns:
            dict: JSON representation of the Advance instance with additional computed fields.
        """
        representation = super().to_representation(instance)
        request = self.context.get("request")
        representation["date"] = (
            instance.date.strftime("%b %d, %Y") if instance.date else None
        )
        representation["photo"] = (
            request.build_absolute_uri(instance.employee.photo.url)
            if instance.employee.photo
            else None
        )
        representation["name"] = instance.employee.name if instance.employee else None
        representation["employee_service_id"] = (
            instance.employee.employee_service_id if instance.employee else None
        )
        representation["employee_service_id_label"] = (
            ["primary", instance.employee.employee_service_id]
            if instance.employee
            else None
        )
        representation["dept_name"] = (
            instance.employee.dept.name if instance.employee.dept else None
        )
        representation["desig_name"] = (
            instance.employee.desig.name if instance.employee.desig else None
        )
        representation["dept"] = (
            instance.employee.dept.id if instance.employee.dept else None
        )
        representation["desig"] = (
            instance.employee.desig.id if instance.employee.desig else None
        )
        representation["advance_due"] = (
            instance.employee.advance_due if instance.employee else None
        )
        return representation
