# Generated by Django 4.2.1 on 2023-09-24 14:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("client_admin", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="preference",
            name="logo",
            field=models.ImageField(blank=True, null=True, upload_to="logo"),
        ),
    ]
