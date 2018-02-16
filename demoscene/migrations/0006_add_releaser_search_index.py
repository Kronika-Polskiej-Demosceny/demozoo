# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-02-16 20:48
from __future__ import unicode_literals

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('demoscene', '0005_accountprofile_user_onetoonefield'),
    ]

    operations = [
        migrations.AddField(
            model_name='releaser',
            name='search_document',
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
        migrations.AddIndex(
            model_name='releaser',
            index=django.contrib.postgres.indexes.GinIndex(fields=[b'search_document'], name='demoscene_r_search__ff7f7c_gin'),
        ),
    ]
