# Generated by Django 3.1 on 2024-03-07 07:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0005_auto_20240307_1250"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderaddress",
            name="pincode",
        ),
    ]
