# Generated by Django 3.1 on 2024-03-05 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("category", "0002_category_is_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
