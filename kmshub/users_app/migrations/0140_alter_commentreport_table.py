# Generated by Django 4.2.7 on 2024-05-14 05:18

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0139_discussionreport_commentreport"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="commentreport",
            table="tbl_comment_report",
        ),
    ]