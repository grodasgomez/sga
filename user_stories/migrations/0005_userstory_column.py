# Generated by Django 4.1 on 2022-10-11 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_stories', '0004_alter_userstory_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstory',
            name='column',
            field=models.IntegerField(default=0),
        ),
    ]
