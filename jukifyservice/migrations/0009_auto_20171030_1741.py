# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-30 17:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jukifyservice', '0008_auto_20171028_1824'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlaylistTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='playlist',
            name='tracks',
        ),
        migrations.AddField(
            model_name='playlist',
            name='url',
            field=models.CharField(default='url.jukify.us', max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='playlisttrack',
            name='playlist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jukifyservice.Playlist'),
        ),
        migrations.AddField(
            model_name='playlisttrack',
            name='track',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jukifyservice.Track'),
        ),
    ]
