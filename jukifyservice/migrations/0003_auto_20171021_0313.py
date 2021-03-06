# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-21 03:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jukifyservice', '0002_auto_20171021_0229'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jukifyservice.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spotify_id', models.CharField(max_length=256)),
                ('name', models.CharField(max_length=256)),
                ('artists', models.CharField(max_length=512)),
                ('preview_url', models.CharField(max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='expires_in',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='last_logged_at',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='display_name',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='user',
            name='spotify_id',
            field=models.CharField(max_length=256),
        ),
        migrations.AddField(
            model_name='playlist',
            name='tracks',
            field=models.ManyToManyField(to='jukifyservice.Track'),
        ),
        migrations.AddField(
            model_name='group',
            name='users',
            field=models.ManyToManyField(to='jukifyservice.User'),
        ),
    ]
