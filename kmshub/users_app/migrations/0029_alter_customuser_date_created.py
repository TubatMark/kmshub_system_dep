# Generated by Django 4.2.7 on 2024-01-18 07:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0028_alter_about_date_created_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="date_created",
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
    ]