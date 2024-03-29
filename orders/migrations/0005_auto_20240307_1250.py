# Generated by Django 3.1 on 2024-03-07 07:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0004_auto_20240305_2037"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrderAddress",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("full_name", models.CharField(max_length=100)),
                ("phone_number", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=254)),
                ("full_address", models.CharField(max_length=200)),
                ("country", models.CharField(max_length=100)),
                ("state", models.CharField(max_length=100)),
                ("city", models.CharField(max_length=100)),
                ("pincode", models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name="order",
            name="address",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="orders.orderaddress",
            ),
        ),
    ]
