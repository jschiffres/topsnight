# Generated by Django 4.1 on 2022-09-05 00:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("TopsListGenerator", "0002_playlist"),
    ]

    operations = [
        migrations.AddField(
            model_name="playlist",
            name="playlistHTML",
            field=models.TextField(blank=True, null=True),
        ),
    ]
