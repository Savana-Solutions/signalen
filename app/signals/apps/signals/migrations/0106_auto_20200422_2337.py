# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2020 - 2021 Gemeente Amsterdam
# Generated by Django 2.2.12 on 2020-04-22 21:37

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0104_auto_20200410_1001'),
    ]

    operations = [
        migrations.CreateModel(
            name='AreaType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=255)),
                ('description', models.TextField(max_length=3000)),
            ],
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=255)),
                ('geometry', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
                ('_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='signals.AreaType')),
            ],
        ),
    ]
