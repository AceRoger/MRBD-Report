# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0001_initial'),
        ('consumerapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('assigned_date', models.DateTimeField(default=django.utils.timezone.now, null=True, blank=True)),
                ('record_status', models.CharField(default=b'ALLOCATED', max_length=20, choices=[(b'ALLOCATED', b'ALLOCATED'), (b'ASSIGNED', b'ASSIGNED'), (b'REASSIGNED', b'REASSIGNED'), (b'COMPLETED', b'COMPLETED'), (b'DEASSIGNED', b'DEASSIGNED'), (b'DUPLICATE', b'DUPLICATE'), (b'REVISIT', b'REVISIT')])),
                ('completion_date', models.DateTimeField(null=True, blank=True)),
                ('reading_month', models.CharField(default=b'201611', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_deleted_for_mr', models.BooleanField(default=False)),
                ('is_reading_completed', models.BooleanField(default=False)),
                ('is_revisit', models.BooleanField(default=False)),
                ('created_by', models.CharField(max_length=50, null=True, blank=True)),
                ('updated_by', models.CharField(max_length=50, null=True, blank=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('Updated_on', models.DateTimeField(null=True, blank=True)),
                ('consumerdetail', models.ForeignKey(to='consumerapp.ConsumerDetails', null=True)),
                ('meterreader', models.ForeignKey(to='adminapp.UserProfile', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MeterReading',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('current_meter_reading', models.CharField(max_length=20, null=True, blank=True)),
                ('image_url', models.URLField(max_length=500, null=True, blank=True)),
                ('reading_status', models.CharField(default=b'validation1', max_length=20, null=True, blank=True, choices=[(b'validation1', b'validation1'), (b'validation2', b'validation2'), (b'complete', b'complete'), (b'revisit', b'revisit')])),
                ('is_assigned_to_v1', models.BooleanField(default=False)),
                ('is_assigned_to_v2', models.BooleanField(default=False)),
                ('longitude', models.CharField(max_length=20, null=True, blank=True)),
                ('latitude', models.CharField(max_length=20, null=True, blank=True)),
                ('is_qr_code_tempered', models.BooleanField(default=False)),
                ('qr_code_image_url', models.URLField(max_length=500, null=True, blank=True)),
                ('reading_month', models.CharField(default=b'201611', max_length=20)),
                ('reading_date', models.DateTimeField(default=django.utils.timezone.now, null=True, blank=True)),
                ('suspicious_activity', models.BooleanField(default=False)),
                ('suspicious_image_url', models.URLField(max_length=500, null=True, blank=True)),
                ('suspicious_activity_remark', models.CharField(max_length=500, null=True, blank=True)),
                ('comment', models.CharField(max_length=500, null=True, blank=True)),
                ('reading_taken_by', models.CharField(default=b'Manual', max_length=20, choices=[(b'Manual', b'Manual'), (b'QRCode', b'QRCode')])),
                ('is_duplicate', models.BooleanField(default=False, choices=[(True, True), (False, False)])),
                ('is_active', models.BooleanField(default=True, choices=[(True, True), (False, False)])),
                ('is_deleted', models.BooleanField(default=False, choices=[(True, True), (False, False)])),
                ('created_by', models.CharField(max_length=50, null=True, blank=True)),
                ('updated_by', models.CharField(max_length=50, null=True, blank=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('Updated_on', models.DateTimeField(null=True, blank=True)),
                ('comment_v1', models.CharField(max_length=500, null=True, blank=True)),
                ('current_meter_reading_v1', models.CharField(max_length=20, null=True, blank=True)),
                ('image_remark_v1', models.CharField(default=b'', max_length=50, null=True, blank=True)),
                ('validated_on_v1', models.DateTimeField(null=True, blank=True)),
                ('comment_v2', models.CharField(max_length=500, null=True, blank=True)),
                ('current_meter_reading_v2', models.CharField(max_length=20, null=True, blank=True)),
                ('image_remark_v2', models.CharField(default=b'', max_length=50, null=True, blank=True)),
                ('validated_on_v2', models.DateTimeField(null=True, blank=True)),
                ('jobcard', models.ForeignKey(to='dispatch.JobCard', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MeterStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('meter_status', models.CharField(default=b'Normal', max_length=20, null=True, blank=True, choices=[(b'Normal', b'Normal'), (b'Faulty', b'Faulty'), (b'LockPremise', b'LockPremise'), (b'ReadingOverflow', b'ReadingOverflow'), (b'MeterChange', b'MeterChange'), (b'Inaccessible', b'Inaccessible'), (b'MeterMissing', b'MeterMissing'), (b'ReadingNotTaken', b'ReadingNotTaken')])),
                ('status_code', models.CharField(max_length=20, null=True, blank=True)),
                ('is_deleted', models.BooleanField(default=False, choices=[(True, True), (False, False)])),
                ('created_by', models.CharField(max_length=50, null=True, blank=True)),
                ('updated_by', models.CharField(max_length=50, null=True, blank=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('Updated_on', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReaderStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reader_status', models.CharField(default=b'Normal', max_length=20, null=True, blank=True, choices=[(b'Normal', b'Normal'), (b'Mechanical', b'Mechanical'), (b'Disconnected', b'Disconnected'), (b'Shifting', b'Shifting'), (b'MeterChanged', b'MeterChanged'), (b'ReadingOverflow', b'ReadingOverflow')])),
                ('status_code', models.CharField(max_length=20, null=True, blank=True)),
                ('is_deleted', models.BooleanField(default=False, choices=[(True, True), (False, False)])),
                ('created_by', models.CharField(max_length=50, null=True, blank=True)),
                ('updated_by', models.CharField(max_length=50, null=True, blank=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('Updated_on', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='RouteAssignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('assign_date', models.DateTimeField(default=django.utils.timezone.now, null=True, blank=True)),
                ('due_date', models.DateTimeField(null=True, blank=True)),
                ('reading_month', models.CharField(default=b'201611', max_length=20)),
                ('is_deleted', models.BooleanField(default=False)),
                ('record_status', models.CharField(default=b'Active', max_length=10, choices=[(b'ACTIVE', b'ACTIVE'), (b'INACTIVE', b'INACTIVE')])),
                ('dispatch_status', models.CharField(default=b'Not Dispatched', max_length=20, null=True, blank=True)),
                ('is_active', models.BooleanField(default=False)),
                ('sent_to_mr', models.BooleanField(default=False)),
                ('is_reading_completed', models.BooleanField(default=False)),
                ('created_by', models.CharField(max_length=50)),
                ('updated_by', models.CharField(max_length=50, null=True, blank=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_on', models.DateTimeField(null=True, blank=True)),
                ('meterreader', models.ForeignKey(blank=True, to='adminapp.UserProfile', null=True)),
                ('routedetail', models.ForeignKey(blank=True, to='adminapp.RouteDetail', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RouteDeassigned',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deassign_date', models.DateTimeField(default=django.utils.timezone.now, null=True, blank=True)),
                ('meterreader', models.ForeignKey(blank=True, to='adminapp.UserProfile', null=True)),
                ('routedetail', models.ForeignKey(blank=True, to='adminapp.RouteDetail', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RouteProcess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reading_month', models.CharField(default=b'201611', max_length=20, null=True, blank=True)),
                ('is_processing', models.BooleanField(default=False)),
                ('routedetail', models.ForeignKey(blank=True, to='adminapp.RouteDetail', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UnbilledConsumerAssignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reading_month', models.CharField(default=b'201611', max_length=20)),
                ('created_by', models.CharField(max_length=50, null=True, blank=True)),
                ('updated_by', models.CharField(max_length=50, null=True, blank=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('Updated_on', models.DateTimeField(null=True, blank=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('unbillconsumer', models.ForeignKey(blank=True, to='consumerapp.UnBilledConsumers', null=True)),
                ('user', models.ForeignKey(related_name='unbilleduser', to='adminapp.UserProfile', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UnbilledConsumerAssignmentCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField(null=True, blank=True)),
                ('user', models.ForeignKey(to='adminapp.UserProfile', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ValidatorAssignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('remark', models.CharField(max_length=200, null=True, blank=True)),
                ('result', models.CharField(max_length=200, null=True, blank=True)),
                ('reading_month', models.CharField(default=b'201611', max_length=20)),
                ('assigned_to', models.CharField(max_length=20, null=True, blank=True)),
                ('created_by', models.CharField(max_length=50, null=True, blank=True)),
                ('updated_by', models.CharField(max_length=50, null=True, blank=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('Updated_on', models.DateTimeField(null=True, blank=True)),
                ('is_validated', models.BooleanField(default=False)),
                ('sent_to_revisit', models.BooleanField(default=False)),
                ('meterreading', models.ForeignKey(to='dispatch.MeterReading', null=True)),
                ('user', models.ForeignKey(related_name='user', to='adminapp.UserProfile', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ValidatorAssignmentCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reading_month', models.CharField(default=b'201611', max_length=20)),
                ('count', models.IntegerField(null=True, blank=True)),
                ('user', models.ForeignKey(to='adminapp.UserProfile', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='meterreading',
            name='meter_status',
            field=models.ForeignKey(to='dispatch.MeterStatus', null=True),
        ),
        migrations.AddField(
            model_name='meterreading',
            name='meter_status_v1',
            field=models.ForeignKey(related_name='meter_status_v1', blank=True, to='dispatch.MeterStatus', null=True),
        ),
        migrations.AddField(
            model_name='meterreading',
            name='meter_status_v2',
            field=models.ForeignKey(related_name='meter_status_v2', blank=True, to='dispatch.MeterStatus', null=True),
        ),
        migrations.AddField(
            model_name='meterreading',
            name='reader_status',
            field=models.ForeignKey(to='dispatch.ReaderStatus', null=True),
        ),
        migrations.AddField(
            model_name='meterreading',
            name='reader_status_v1',
            field=models.ForeignKey(related_name='reader_status_v1', blank=True, to='dispatch.ReaderStatus', null=True),
        ),
        migrations.AddField(
            model_name='meterreading',
            name='reader_status_v2',
            field=models.ForeignKey(related_name='reader_status_v2', blank=True, to='dispatch.ReaderStatus', null=True),
        ),
        migrations.AddField(
            model_name='meterreading',
            name='updated_by_v1',
            field=models.ForeignKey(related_name='v1', blank=True, to='adminapp.UserProfile', null=True),
        ),
        migrations.AddField(
            model_name='meterreading',
            name='updated_by_v2',
            field=models.ForeignKey(related_name='v2', blank=True, to='adminapp.UserProfile', null=True),
        ),
        migrations.AddField(
            model_name='jobcard',
            name='routeassigned',
            field=models.ForeignKey(to='dispatch.RouteAssignment', null=True),
        ),
    ]