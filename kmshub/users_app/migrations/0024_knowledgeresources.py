# Generated by Django 4.2.7 on 2024-01-16 07:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0023_rename_date_comment_date_commented"),
    ]

    operations = [
        migrations.CreateModel(
            name="KnowledgeResources",
            fields=[
                ("knowledge_id", models.AutoField(primary_key=True, serialize=False)),
                ("knowledge_title", models.CharField(max_length=255)),
                ("knowledge_description", models.TextField()),
                ("commodity", models.ManyToManyField(to="users_app.commodity")),
            ],
            options={
                "db_table": "tbl_knowledge",
            },
        ),
    ]