# Generated by Django 4.2.7 on 2024-01-04 03:36

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0007_searchfrequency_and_more"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="about",
            table="tbl_about",
        ),
        migrations.AlterModelTable(
            name="commodity",
            table="tbl_commodity",
        ),
        migrations.AlterModelTable(
            name="discussion",
            table="tbl_discussion&forum",
        ),
        migrations.AlterModelTable(
            name="reply",
            table="tbl_reply",
        ),
        migrations.AlterModelTable(
            name="searchfrequency",
            table="tbl_search_analytics",
        ),
    ]