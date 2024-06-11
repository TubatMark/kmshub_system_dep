# Generated by Django 4.2.7 on 2024-03-26 05:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0112_remove_uploadvideo_video_path_uploadvideo_url"),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
            ],
            options={
                "db_table": "tbl_events",
            },
        ),
    ]