# Generated by Django 4.2.7 on 2024-01-18 07:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0026_customuser_date_created"),
    ]

    operations = [
        migrations.AlterField(
            model_name="about",
            name="date_created",
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="commodity",
            name="date_created",
            field=models.DateField(default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name="commodity",
            name="date_edited",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="date_created",
            field=models.DateField(default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name="knowledgeresources",
            name="date_created",
            field=models.DateField(default=django.utils.timezone.now, null=True),
        ),
    ]