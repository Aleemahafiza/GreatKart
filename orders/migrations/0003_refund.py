# Generated by Django 3.1 on 2024-03-05 15:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_auto_20240225_1125"),
    ]

    operations = [
        migrations.CreateModel(
            name="Refund",
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
                ("reason", models.TextField()),
                ("accepted", models.BooleanField(default=False)),
                ("email", models.EmailField(max_length=254)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="orders.order",
                    ),
                ),
            ],
        ),
    ]
