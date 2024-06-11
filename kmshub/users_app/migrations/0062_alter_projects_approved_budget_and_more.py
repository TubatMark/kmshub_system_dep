# Generated by Django 4.2.7 on 2024-01-31 06:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0061_alter_projects_number_years"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projects",
            name="approved_budget",
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name="projects",
            name="fund_source",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="projects",
            name="number_years",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="projects",
            name="project_status",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="projects",
            name="project_title",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="projects",
            name="proponent",
            field=models.CharField(max_length=255),
        ),
    ]