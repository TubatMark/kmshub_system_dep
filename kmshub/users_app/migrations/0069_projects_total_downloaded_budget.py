# Generated by Django 4.2.7 on 2024-02-01 05:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0068_programs_program_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="projects",
            name="total_downloaded_budget",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
