# Generated by Django 4.2.7 on 2024-01-31 06:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0060_alter_projects_approved_budget_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projects",
            name="number_years",
            field=models.IntegerField(default=0, null=True),
        ),
    ]