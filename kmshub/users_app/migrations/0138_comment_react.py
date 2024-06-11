# Generated by Django 4.2.7 on 2024-05-13 05:52

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0137_commentrating_discussionrating_delete_reaction"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="react",
            field=models.ManyToManyField(
                blank=True,
                related_name="user_react_comment",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]