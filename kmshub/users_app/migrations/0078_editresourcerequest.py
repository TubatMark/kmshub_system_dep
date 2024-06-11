# Generated by Django 4.2.7 on 2024-02-12 01:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0077_resources_is_pending_edit"),
    ]

    operations = [
        migrations.CreateModel(
            name="EditResourceRequest",
            fields=[
                ("editRequest_id", models.AutoField(primary_key=True, serialize=False)),
                ("edited_title", models.CharField(max_length=255)),
                ("edited_description", models.TextField()),
                (
                    "edited_file",
                    models.FileField(
                        blank=True, null=True, upload_to="edits/resources/"
                    ),
                ),
                (
                    "edited_images",
                    models.ImageField(
                        blank=True, null=True, upload_to="edits/resources/"
                    ),
                ),
                (
                    "edited_latitude",
                    models.DecimalField(
                        blank=True, decimal_places=6, max_digits=9, null=True
                    ),
                ),
                (
                    "edited_longitude",
                    models.DecimalField(
                        blank=True, decimal_places=6, max_digits=9, null=True
                    ),
                ),
                ("edited_link", models.URLField(blank=True, null=True)),
                ("date_submitted", models.DateTimeField(auto_now_add=True)),
                ("is_approved", models.BooleanField(default=False)),
                ("edited_cmi", models.ManyToManyField(blank=True, to="users_app.cmi")),
                (
                    "edited_commodity",
                    models.ManyToManyField(blank=True, to="users_app.commodity"),
                ),
                (
                    "edited_knowledge",
                    models.ManyToManyField(
                        blank=True, to="users_app.knowledgeresources"
                    ),
                ),
                (
                    "resource",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="users_app.resources",
                    ),
                ),
            ],
            options={
                "db_table": "tbl_request_edit",
            },
        ),
    ]