# Generated by Django 4.2.7 on 2024-03-26 07:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0114_delete_event"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="feedback",
            field=models.BooleanField(default=False),
        ),
    ]
