# Generated by Django 4.2.7 on 2024-01-12 06:45

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0021_comment_delete_reply"),
    ]

    operations = [
        migrations.RenameField(
            model_name="comment",
            old_name="discussion_id",
            new_name="discussion",
        ),
    ]
