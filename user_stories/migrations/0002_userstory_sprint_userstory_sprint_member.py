# Generated by Django 4.1 on 2022-09-24 00:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sprints', '0002_sprintmember'),
        ('user_stories', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstory',
            name='sprint',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sprints.sprint'),
        ),
        migrations.AddField(
            model_name='userstory',
            name='sprint_member',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sprints.sprintmember'),
        ),
    ]
