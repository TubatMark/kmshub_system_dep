# Generated by Django 4.2.7 on 2024-02-15 00:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0089_resources_contact_num_resources_farm"),
    ]

    operations = [
        migrations.CreateModel(
            name="UsefulLinks",
            fields=[
                ("link_id", models.AutoField(primary_key=True, serialize=False)),
                ("link_title", models.CharField(max_length=255, null=True)),
                ("link", models.URLField(blank=True, null=True)),
            ],
            options={
                "db_table": "tbl_useful_links",
            },
        ),
    ]
