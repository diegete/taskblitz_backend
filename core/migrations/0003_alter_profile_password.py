# Generated by Django 4.1.2 on 2024-08-26 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_profile_last_name_profile_name_profile_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='password',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
