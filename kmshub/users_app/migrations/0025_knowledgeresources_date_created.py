# Generated by Django 4.2.7 on 2024-01-16 07:55

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0024_knowledgeresources"),
    ]

    operations = [
        migrations.AddField(
            model_name="knowledgeresources",
            name="date_created",
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
    ]
