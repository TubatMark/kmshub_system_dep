# Generated by Django 4.2.7 on 2024-01-19 05:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0033_alter_customuser_user_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="discussion",
            name="author",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]