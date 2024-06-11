# Generated by Django 4.2.7 on 2024-02-05 02:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0072_remove_knowledgeresources_commodity_resources"),
    ]

    operations = [
        migrations.AddField(
            model_name="resources",
            name="images",
            field=models.ImageField(blank=True, null=True, upload_to="resources/"),
        ),
        migrations.AddField(
            model_name="resources",
            name="user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="customuser",
            name="user_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("expert", "Expert"),
                    ("secretariat", "Secretariat"),
                    ("general", "General User"),
                    ("admin", "Admin User"),
                    ("cmi", "CMI"),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]