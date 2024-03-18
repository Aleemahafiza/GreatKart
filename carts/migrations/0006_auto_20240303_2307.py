# Generated by Django 3.1 on 2024-03-03 17:37

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("carts", "0005_cart_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cart",
            name="cart_id",
            field=models.CharField(
                default=uuid.uuid4, max_length=250, unique=True
            ),
        ),
    ]
