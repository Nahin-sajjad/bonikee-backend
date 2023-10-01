from rest_framework import generics

from apps.users.models import User
from apps.users.serializers.user_list import UserListSerializer


class UserListView(generics.ListAPIView):
    """
    API view for listing users.
    """

    queryset = User.objects.all()  # Queryset to fetch all users from the database
    serializer_class = UserListSerializer  # Serializer class to serialize user data

    # Additional view customization can be added here if needed
