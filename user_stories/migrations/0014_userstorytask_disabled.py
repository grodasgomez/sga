# Generated by Django 4.1 on 2022-11-04 00:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_stories', '0013_remove_userstory_hours_worked'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstorytask',
            name='disabled',
            field=models.BooleanField(default=False),
        ),
    ]
