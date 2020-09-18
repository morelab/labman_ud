# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2019-01-16 13:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import entities.datasets.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('persons', '0003_person_projects'),
        ('projects', '0009_merge'),
        ('utils', '0004_auto_20150930_1056'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=250, unique=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(blank=True, max_length=1000, null=True, upload_to=entities.datasets.models.dataset_path)),
                ('format', models.CharField(choices=[(b'ext', b'External link'), (b'csv', b'*.csv'), (b'zip', b'*.zip'), (b'xls', b'*.xls'), (b'xlsx', b'*.xlsx'), (b'xlm', b'*.xlm'), (b'json', b'*.json'), (b'geojson', b'*.geojson'), (b'jpeg', b'*.jpeg'), (b'kml', b'*.kml'), (b'shp', b'*.shp'), (b'sql', b'*.sql'), (b'R', b'*.R'), (b'jsonld', b'*.jsonld'), (b'dat', b'*.dat')], default=b'ext', max_length=50)),
                ('main_webpage', models.URLField(blank=True, max_length=250, null=True)),
                ('external_download_url', models.URLField(blank=True, max_length=250, null=True)),
                ('notes', models.TextField(max_length=25000)),
                ('license', models.CharField(blank=True, choices=[(b'ne', b'Not specified'), (b'gpl', b'General Public License'), (b'odc', b'Open Data Commons'), (b'cc', b'Creative Commons'), (b'ogl', b'Open Government License'), (b'ncgl', b'Non-Commercial Government Licence'), (b'pd', b'Public Domain'), (b'mit', b'MIT License'), (b'ap', b'Apache Public License')], default=b'ne', max_length=50)),
                ('version', models.FloatField(default=1.0)),
                ('doi', models.URLField(blank=True, max_length=250, null=True)),
            ],
            options={
                'ordering': ['-slug'],
                'verbose_name': 'Dataset',
                'verbose_name_plural': 'Datasets',
            },
        ),
        migrations.CreateModel(
            name='DatasetAuthor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveIntegerField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='persons.Person')),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='datasets.Dataset')),
            ],
            options={
                'verbose_name': 'Dataset author',
                'verbose_name_plural': 'Dataset authors',
            },
        ),
        migrations.CreateModel(
            name='DatasetProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='datasets.Dataset')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.Project')),
            ],
            options={
                'verbose_name': 'Dataset project',
                'verbose_name_plural': 'Dataset projects',
            },
        ),
        migrations.CreateModel(
            name='DatasetTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='datasets.Dataset')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='utils.Tag')),
            ],
            options={
                'ordering': ['tag__slug'],
            },
        ),
        migrations.AddField(
            model_name='dataset',
            name='authors',
            field=models.ManyToManyField(related_name='dataset_authors', through='datasets.DatasetAuthor', to='persons.Person'),
        ),
        migrations.AddField(
            model_name='dataset',
            name='projects',
            field=models.ManyToManyField(related_name='dataset_projects', through='datasets.DatasetProject', to='projects.Project'),
        ),
        migrations.AddField(
            model_name='dataset',
            name='tags',
            field=models.ManyToManyField(through='datasets.DatasetTag', to='utils.Tag'),
        ),
    ]