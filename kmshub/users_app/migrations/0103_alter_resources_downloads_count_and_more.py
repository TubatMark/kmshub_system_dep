# Generated by Django 4.2.7 on 2024-03-05 02:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "users_app",
            "0102_resources_downloads_count_resources_reactions_count_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="resources",
            name="downloads_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="resources",
            name="reactions_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="resources",
            name="shares_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="resources",
            name="views_count",
            field=models.PositiveIntegerField(default=0),
        ),
    ]