from rest_framework.generics import UpdateAPIView

from apps.users.models import User
from apps.users.serializers.user_list import UserListSerializer


class UpdateUserInformationView(UpdateAPIView):
    """
    API view for updating user information.
    """

    queryset = User.objects.all().order_by(
        "date_joined"
    )  # Queryset to fetch all users and order them by date joined
    serializer_class = (
        UserListSerializer  # Serializer class to serialize user data for updating
    )

    # Additional view customization can be added here if needed
