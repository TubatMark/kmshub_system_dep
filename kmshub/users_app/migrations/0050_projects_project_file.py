# Generated by Django 4.2.7 on 2024-01-29 06:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0049_projects"),
    ]

    operations = [
        migrations.AddField(
            model_name="projects",
            name="project_file",
            field=models.FileField(null=True, upload_to="projects/"),
        ),
    ]