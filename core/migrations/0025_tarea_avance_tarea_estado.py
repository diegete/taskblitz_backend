# Generated by Django 4.1.2 on 2024-10-24 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_tarea_fechainicio'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarea',
            name='avance',
            field=models.CharField(choices=[('iniciada', 'Iniciada'), ('en curso', 'En Curso'), ('finalizada', 'Finalizada')], max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='tarea',
            name='estado',
            field=models.BooleanField(null=True),
        ),
    ]
