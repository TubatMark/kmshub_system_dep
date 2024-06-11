# Generated by Django 4.2.7 on 2024-01-24 05:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0044_alter_commodity_resources_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="discussion",
            name="commodity_id",
            field=models.ManyToManyField(
                related_name="tag_commodity", to="users_app.commodity"
            ),
        ),
    ]