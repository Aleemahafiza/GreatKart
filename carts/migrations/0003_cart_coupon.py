# Generated by Django 3.1 on 2024-03-03 06:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0003_coupon"),
        ("carts", "0002_auto_20240225_1125"),
    ]

    operations = [
        migrations.AddField(
            model_name="cart",
            name="coupon",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="store.coupon",
            ),
        ),
    ]