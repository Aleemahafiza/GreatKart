# Generated by Django 3.1 on 2024-03-02 06:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_account_wallet"),
    ]

    operations = [
        migrations.CreateModel(
            name="Address",
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
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                ("phone", models.CharField(blank=True, max_length=50)),
                ("email", models.EmailField(max_length=50)),
                (
                    "address_line_1",
                    models.CharField(max_length=255, null=True),
                ),
                (
                    "address_line_2",
                    models.CharField(
                        blank=True, max_length=255, null=True
                    ),
                ),
                (
                    "country",
                    models.CharField(blank=True, max_length=50),
                ),
                ("state", models.CharField(blank=True, max_length=50)),
                ("city", models.CharField(blank=True, max_length=50)),
                (
                    "pincode",
                    models.CharField(blank=True, max_length=50),
                ),
                (
                    "order_note",
                    models.CharField(
                        blank=True, max_length=100, null=True
                    ),
                ),
                (
                    "is_available",
                    models.BooleanField(default=True, null=True),
                ),
                (
                    "is_saved_address",
                    models.BooleanField(default=False),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
