# Generated by Django 4.2.1 on 2023-09-27 10:17

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "client_admin",
            "0004_alter_preference_admin_alter_preference_finance_and_more",
        ),
    ]

    operations = [
        migrations.DeleteModel(
            name="Preference",
        ),
    ]
