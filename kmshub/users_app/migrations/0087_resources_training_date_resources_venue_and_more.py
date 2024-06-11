# Generated by Django 4.2.7 on 2024-02-14 05:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0086_alter_editresourcerequest_edited_cmi_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="resources",
            name="training_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="resources",
            name="venue",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="resources",
            name="webinar_link",
            field=models.URLField(blank=True, null=True),
        ),
    ]
