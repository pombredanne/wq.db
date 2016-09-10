# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-12 03:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AnnotatedModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AnotherRelatedModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CustomAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='CustomPatternModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='CustomType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='CustomTypedAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='CustomTypedPatternModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='IdentifiedAnnotatedModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, db_index=True, max_length=255)),
                ('slug', models.CharField(blank=True, max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IdentifiedMarkedModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, db_index=True, max_length=255)),
                ('slug', models.CharField(blank=True, max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IdentifiedModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, db_index=True, max_length=255)),
                ('slug', models.CharField(blank=True, max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='IdentifiedRelatedModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, db_index=True, max_length=255)),
                ('slug', models.CharField(blank=True, max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LocatedModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MarkedModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ModelWithNaturalKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='NaturalKeyChild',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='NaturalKeyParent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
                ('group', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='RelatedModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='naturalkeyparent',
            unique_together=set([('code', 'group')]),
        ),
        migrations.AddField(
            model_name='naturalkeychild',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patterns_app.NaturalKeyParent'),
        ),
        migrations.AddField(
            model_name='modelwithnaturalkey',
            name='key',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patterns_app.NaturalKeyChild'),
        ),
        migrations.AlterUniqueTogether(
            name='identifiedmodel',
            unique_together=set([('slug',)]),
        ),
        migrations.AddField(
            model_name='customtypedattachment',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='patterns_app.CustomTypedPatternModel'),
        ),
        migrations.AddField(
            model_name='customtypedattachment',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patterns_app.CustomType'),
        ),
        migrations.AddField(
            model_name='customattachment',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='patterns_app.CustomPatternModel'),
        ),
        migrations.AlterUniqueTogether(
            name='naturalkeychild',
            unique_together=set([('parent', 'mode')]),
        ),
    ]