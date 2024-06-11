# Generated by Django 4.2.7 on 2024-04-16 03:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0123_cmiteam"),
    ]

    operations = [
        migrations.AddField(
            model_name="commodity",
            name="latitude",
            field=models.DecimalField(
                blank=True, decimal_places=6, max_digits=9, null=True
            ),
        ),
        migrations.AddField(
            model_name="commodity",
            name="longitude",
            field=models.DecimalField(
                blank=True, decimal_places=6, max_digits=9, null=True
            ),
        ),
    ]