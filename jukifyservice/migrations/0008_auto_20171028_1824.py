# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-28 18:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jukifyservice', '0007_auto_20171028_1823'),
    ]

    operations = [
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='group',
            name='a',
        ),
        migrations.AddField(
            model_name='membership',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jukifyservice.Group'),
        ),
        migrations.AddField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jukifyservice.User'),
        ),
        migrations.AddField(
            model_name='group',
            name='users',
            field=models.ManyToManyField(through='jukifyservice.Membership', to='jukifyservice.User'),
        ),
    ]