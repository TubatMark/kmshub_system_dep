# Generated by Django 4.2.7 on 2024-01-22 03:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0037_remove_comment_commentor"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="commentor",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]