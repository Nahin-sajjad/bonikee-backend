from django.db import models
from apps.clients.models import ClientModel
from django.contrib.auth import get_user_model
from apps.share.request_middleware import request_local

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    tenant = models.ForeignKey(
        ClientModel,
        on_delete=models.CASCADE,
        related_name="%(class)s_base_models",
        blank=True,
        null=True,
    )

    created_by = models.ForeignKey(
        User,
        related_name="%(class)s_created_models",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    updated_by = models.ForeignKey(
        User,
        related_name="%(class)s_updated_models",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Check if there's a request object in the thread-local storage
        request = getattr(request_local, "request", None)
        if request:
            try:
                user = request.user
                tenant = request.tenant
                if not self.created_by:
                    self.created_by = user
                if not self.updated_by:
                    self.updated_by = user
                if not tenant:
                    self.tenant = tenant
            except:
                pass

        super().save(*args, **kwargs)
