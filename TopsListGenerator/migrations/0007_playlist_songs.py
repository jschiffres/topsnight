# Generated by Django 4.1 on 2022-09-09 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("TopsListGenerator", "0006_delete_group"),
    ]

    operations = [
        migrations.AddField(
            model_name="playlist",
            name="songs",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]