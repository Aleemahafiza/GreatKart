# Generated by Django 3.1 on 2024-03-05 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_refund"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="refund_granted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="order",
            name="refund_requested",
            field=models.BooleanField(default=False),
        ),
    ]
