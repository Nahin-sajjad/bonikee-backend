from django.db import models
from django.contrib.auth import get_user_model
from django_tenants.models import TenantMixin, DomainMixin
import uuid

# Get the User model specified in Django's settings
User = get_user_model()

class ClientModel(TenantMixin):
    """
    Model representing a tenant or client in a multi-tenant application.

    This model extends the TenantMixin provided by django_tenants.

    Attributes:
        id (UUIDField): Primary key for the tenant, automatically generated.
        tenant_name (CharField): The name of the tenant.
        paid_until (DateField): Date until which the tenant has paid.
        on_trial (BooleanField): Indicates whether the tenant is on a trial period.
        established_on (DateField): Date when the tenant was established.

    Note:
        The 'auto_create_schema' attribute is set to False to disable automatic schema creation.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_name = models.CharField(max_length=250, blank=True, null=True)
    schema_name = models.CharField(max_length=63, db_index=True)
    paid_until = models.DateField()
    on_trial = models.BooleanField(default=False)
    established_on = models.DateField(auto_now_add=True, blank=True, null=True)

    auto_create_schema = False

    def save(self, *args, **kwargs):
        if self.schema_name != 'public' and self.schema_name != 'tenants':
            self.schema_name = 'tenants'
        super(ClientModel, self).save(*args, **kwargs)

    def __str__(self):
        return self.tenant_name


class DomainModel(DomainMixin):
    """
    Model representing a domain for a tenant.

    This model extends the DomainMixin provided by django_tenants.
    It inherits fields and methods for managing domains.
    """
    pass

class TenantUser(models.Model):
    """
    Model representing a user associated with a tenant.

    This model links a user from the User model with a specific tenant.

    Attributes:
        user (ForeignKey): Reference to the User associated with the tenant user.
        tenant (ForeignKey): Reference to the ClientModel (tenant) associated with the user.
        is_superuser (BooleanField): Indicates if the user is a superuser for the tenant.

    Meta:
        db_table (str): The database table name for the TenantUser model.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_tenant_users")
    tenant = models.ForeignKey(
        ClientModel, on_delete=models.CASCADE, related_name="tenant_tenant_users")
    is_superuser = models.BooleanField(default=False)

    class Meta:
        db_table = "TenantUser"

    def __str__(self):
        return self.tenant.tenant_name
