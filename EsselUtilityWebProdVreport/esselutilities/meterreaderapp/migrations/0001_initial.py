# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company_name', models.CharField(max_length=500)),
                ('device_name', models.CharField(max_length=500)),
                ('make', models.CharField(max_length=500)),
                ('imei_no', models.CharField(max_length=500)),
                ('is_deleted', models.CharField(default=b'NO', max_length=20, choices=[(b'YES', b'YES'), (b'NO', b'NO')])),
                ('device_details_created_by', models.CharField(max_length=500)),
                ('device_details_updated_by', models.CharField(max_length=500, null=True, blank=True)),
                ('device_details_created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('device_details_updated_date', models.DateTimeField(null=True, blank=True)),
                ('user_id', models.ForeignKey(blank=True, to='adminapp.UserProfile', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PreferredBillCycle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bill_cycle_code', models.CharField(max_length=255, null=True, blank=True)),
                ('preference_no', models.CharField(max_length=20, null=True, blank=True)),
                ('PreferredBillCycle_created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('PreferredBillCycle_updated_date', models.DateTimeField(null=True, blank=True)),
                ('user', models.ForeignKey(blank=True, to='adminapp.UserProfile', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PreferredRoutes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bill_cycle_code', models.CharField(max_length=255, null=True, blank=True)),
                ('route', models.CharField(max_length=255, null=True, blank=True)),
                ('preference_no', models.CharField(max_length=20, null=True, blank=True)),
                ('is_deleted', models.CharField(default=b'NO', max_length=20, choices=[(b'YES', b'YES'), (b'NO', b'NO')])),
                ('preferredroutes_created_by', models.CharField(max_length=500, null=True, blank=True)),
                ('preferredroutes_updated_by', models.CharField(max_length=500, null=True, blank=True)),
                ('preferredroutes_created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('preferredroutes_updated_date', models.DateTimeField(null=True, blank=True)),
                ('user', models.ForeignKey(blank=True, to='adminapp.UserProfile', null=True)),
            ],
        ),
    ]
