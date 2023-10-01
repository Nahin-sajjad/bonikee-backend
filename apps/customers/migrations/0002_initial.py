# Generated by Django 4.2.1 on 2023-09-21 12:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("customers", "0001_initial"),
        ("clients", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)s_created_models",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="customer",
            name="tenant",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s_base_models",
                to="clients.clientmodel",
            ),
        ),
        migrations.AddField(
            model_name="customer",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)s_updated_models",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]