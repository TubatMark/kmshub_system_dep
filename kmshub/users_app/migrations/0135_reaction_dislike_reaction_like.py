# Generated by Django 4.2.7 on 2024-05-10 02:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "users_app",
            "0134_rename_dislike_reaction_rating_remove_reaction_like_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="reaction",
            name="dislike",
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name="reaction",
            name="like",
            field=models.IntegerField(default=1),
        ),
    ]