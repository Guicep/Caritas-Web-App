# Generated by Django 5.0.4 on 2024-05-24 13:09

import createuser.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Publicacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('categoria', models.CharField(max_length=100)),
                ('fecha_publicacion', models.DateField(auto_now=True)),
                ('foto', models.ImageField(blank=True, null=True, upload_to='static/images/')),
                ('descripcion', models.CharField(max_length=200)),
                ('id_usuario', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('correo', models.EmailField(blank=True, max_length=50, unique=True)),
                ('nombre', models.CharField(max_length=30)),
                ('apellido', models.CharField(max_length=20)),
                ('nacimiento', models.DateField()),
                ('dni', models.CharField(max_length=8)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', createuser.models.CustomUserManager()),
            ],
        ),
    ]
