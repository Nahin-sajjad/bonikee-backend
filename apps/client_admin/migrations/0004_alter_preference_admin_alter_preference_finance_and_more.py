# Generated by Django 4.2.1 on 2023-09-25 11:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "client_admin",
            "0003_alter_preference_admin_alter_preference_finance_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="preference",
            name="admin",
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name="preference",
            name="finance",
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name="preference",
            name="invoice",
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name="preference",
            name="product",
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name="preference",
            name="purchase",
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
