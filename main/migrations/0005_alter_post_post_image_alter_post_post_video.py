# Generated by Django 5.1.2 on 2024-10-25 17:07

import main.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0004_alter_user_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="post_image",
            field=models.ImageField(null=True, upload_to=main.models.post_media_path),
        ),
        migrations.AlterField(
            model_name="post",
            name="post_video",
            field=models.FileField(null=True, upload_to=main.models.post_media_path),
        ),
    ]
