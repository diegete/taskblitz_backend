# Generated by Django 4.1.2 on 2024-08-27 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_profile_email_remove_profile_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='email',
            field=models.EmailField(max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='password',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
