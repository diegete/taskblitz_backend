# Generated by Django 5.1.2 on 2024-11-16 02:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_profile_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='image',
        ),
    ]