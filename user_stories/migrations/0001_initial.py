# Generated by Django 4.1 on 2022-09-23 21:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0008_alter_role_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserStory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('business_value', models.IntegerField()),
                ('technical_priority', models.IntegerField()),
                ('estimation_time', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(null=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
                ('us_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.userstorytype')),
            ],
        ),
    ]
