# Generated by Django 4.1 on 2022-11-04 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sprints', '0002_sprintmember'),
    ]

    operations = [
        migrations.AddField(
            model_name='sprint',
            name='estimated_end_date',
            field=models.DateField(null=True),
        ),
    ]