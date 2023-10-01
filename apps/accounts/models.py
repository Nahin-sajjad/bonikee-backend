from django.contrib.auth.models import Group as BaseGroup, Permission
from django.db import models
from apps.share.models.base_model import BaseModel
from django.contrib.auth import get_user_model

# Get the User model specified in Django's settings
User = get_user_model()

class CustomGroup(BaseModel):
    """
    Custom group model for managing user permissions.

    This model extends the base Group model provided by Django's authentication system.

    Attributes:
        name (CharField): The name of the custom group.
        permissions (ManyToManyField): Many-to-many relationship with Permission model.
            Used to associate permissions with this group.
        users (ManyToManyField): Many-to-many relationship with User model.
            Represents the users belonging to this group.

    Methods:
        add_permissions(*permissions): Adds permissions to this group.

    Meta:
        unique_together (tuple): Ensures uniqueness of group names within a tenant.
    """

    name = models.CharField("name", max_length=150)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name="permissions",
        blank=True,
    )

    users = models.ManyToManyField(User, related_name="permission_users", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (
            "name",
            "tenant",
        )

    def add_permissions(self, *permissions):
        """
        Add permissions to this custom group.

        Args:
            *permissions: Variable number of permission objects or codenames as strings.
        """
        for permission in permissions:
            if isinstance(permission, str):
                perm = Permission.objects.get(codename=permission)
            else:
                perm = permission
            self.permissions.add(perm)

    @classmethod
    def get_groups_for_user(cls, user):
        return cls.objects.filter(users=user)
