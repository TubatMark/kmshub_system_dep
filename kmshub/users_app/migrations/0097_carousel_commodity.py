# Generated by Django 4.2.7 on 2024-02-21 06:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0096_carousel_alt"),
    ]

    operations = [
        migrations.AddField(
            model_name="carousel",
            name="commodity",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="users_app.commodity",
            ),
        ),
    ]