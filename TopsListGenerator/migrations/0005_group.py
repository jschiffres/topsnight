# Generated by Django 4.1 on 2022-09-05 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("TopsListGenerator", "0004_topsgroup_delete_group_playlist_groups"),
    ]

    operations = [
        migrations.CreateModel(
            name="Group",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("song_limit", models.PositiveIntegerField()),
            ],
        ),
    ]
