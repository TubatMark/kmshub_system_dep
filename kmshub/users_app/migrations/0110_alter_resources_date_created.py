# Generated by Django 4.2.7 on 2024-03-13 08:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0109_resources_bookmark"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resources",
            name="date_created",
            field=models.DateField(
                blank=True, default=django.utils.timezone.now, null=True
            ),
        ),
    ]
