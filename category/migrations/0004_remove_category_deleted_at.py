# Generated by Django 3.1 on 2024-03-05 11:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("category", "0003_category_deleted_at"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="category",
            name="deleted_at",
        ),
    ]
