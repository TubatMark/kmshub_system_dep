# Generated by Django 4.2.7 on 2024-01-12 01:01

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0018_rename_commodity_tag_discussion_commodity_id"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="reaction",
            table="tbl_reaction",
        ),
    ]