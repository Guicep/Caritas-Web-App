# Generated by Django 5.0.4 on 2024-05-07 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('createuser', '0006_delete_publicacion_delete_todoitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Publicacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('foto', models.ImageField(upload_to='')),
                ('descripcion', models.CharField(max_length=200)),
                ('id_usuario', models.IntegerField()),
            ],
        ),
    ]