# Generated by Django 4.2.7 on 2024-02-12 01:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0076_resources_link"),
    ]

    operations = [
        migrations.AddField(
            model_name="resources",
            name="is_pending_edit",
            field=models.BooleanField(default=False),
        ),
    ]