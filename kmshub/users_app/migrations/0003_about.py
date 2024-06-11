# Generated by Django 4.2.7 on 2024-01-03 05:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0002_commodity"),
    ]

    operations = [
        migrations.CreateModel(
            name="About",
            fields=[
                ("about_id", models.AutoField(primary_key=True, serialize=False)),
                ("content", models.TextField()),
                ("date_created", models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                "db_table": "about_table",
            },
        ),
    ]
