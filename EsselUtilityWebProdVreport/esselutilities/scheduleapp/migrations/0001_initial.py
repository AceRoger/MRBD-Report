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
            name='BillSchedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('month', models.CharField(default=b'201611', max_length=20)),
                ('created_by', models.CharField(max_length=500)),
                ('updated_by', models.CharField(max_length=500, null=True, blank=True)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_date', models.DateTimeField(null=True, blank=True)),
                ('is_imported', models.BooleanField(default=False, choices=[(True, True), (False, False)])),
                ('is_uploaded', models.BooleanField(default=False, choices=[(True, True), (False, False)])),
                ('is_deleted', models.BooleanField(default=False, choices=[(True, True), (False, False)])),
                ('bill_cycle', models.ForeignKey(blank=True, to='adminapp.BillCycle', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BillScheduleApprovalDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'Pending Approval', max_length=500, choices=[(b'Not Confirmed', b'Not Confirmed'), (b'Confirmed', b'Confirmed'), (b'Pending Approval', b'Pending Approval'), (b'Rejected', b'Rejected')])),
                ('remark', models.CharField(max_length=500)),
                ('send_date', models.DateField(null=True, blank=True)),
                ('approval_date', models.DateField(null=True, blank=True)),
                ('created_by', models.CharField(max_length=500)),
                ('updated_by', models.CharField(max_length=500, null=True, blank=True)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_date', models.DateTimeField(null=True, blank=True)),
                ('is_deleted', models.BooleanField(default=False, choices=[(True, True), (False, False)])),
                ('approval_details', models.ForeignKey(blank=True, to='adminapp.ApprovalDetails', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BillScheduleDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField(null=True, blank=True)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('accounting_date', models.DateField(null=True, blank=True)),
                ('estimated_date', models.DateField(null=True, blank=True)),
                ('month', models.CharField(default=b'201611', max_length=20)),
                ('version', models.CharField(default=b'0', max_length=500, null=True)),
                ('status', models.CharField(default=b'Not Confirmed', max_length=500, choices=[(b'Not Confirmed', b'Not Confirmed'), (b'Confirmed', b'Confirmed'), (b'Pending Approval', b'Pending Approval'), (b'Rejected', b'Rejected')])),
                ('last_confirmed', models.BooleanField(default=False, choices=[(True, True), (False, False)])),
                ('is_original', models.BooleanField(default=False, choices=[(True, True), (False, False)])),
                ('is_active', models.BooleanField(default=True, choices=[(True, True), (False, False)])),
                ('created_by', models.CharField(max_length=500)),
                ('updated_by', models.CharField(max_length=500, null=True, blank=True)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_date', models.DateTimeField(null=True, blank=True)),
                ('is_deleted', models.BooleanField(default=False, choices=[(True, True), (False, False)])),
                ('billSchedule', models.ForeignKey(blank=True, to='scheduleapp.BillSchedule', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PN33Download',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('month', models.CharField(default=b'201611', max_length=20)),
                ('start_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('asy_job_id', models.CharField(max_length=100, null=True, blank=True)),
                ('download_status', models.CharField(default=b'Not Started', max_length=500, choices=[(b'Not Started', b'Not Started'), (b'Started', b'Started'), (b'Failed', b'Failed'), (b'Completed', b'Completed')])),
                ('created_by', models.CharField(max_length=500)),
                ('updated_by', models.CharField(max_length=500, null=True, blank=True)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_date', models.DateTimeField(null=True, blank=True)),
                ('is_deleted', models.BooleanField(default=False, choices=[(True, True), (False, False)])),
                ('bill_schedule', models.ForeignKey(blank=True, to='scheduleapp.BillSchedule', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UploadB30',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('month', models.CharField(default=b'201611', max_length=20)),
                ('start_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('asy_job_id', models.CharField(max_length=100, null=True, blank=True)),
                ('status', models.CharField(default=b'Not Started', max_length=500, choices=[(b'Not Started', b'Not Started'), (b'Started', b'Started'), (b'Failed', b'Failed'), (b'Completed', b'Completed')])),
                ('created_by', models.CharField(max_length=500)),
                ('updated_by', models.CharField(max_length=500, null=True, blank=True)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_date', models.DateTimeField(null=True, blank=True)),
                ('is_deleted', models.BooleanField(default=False, choices=[(True, True), (False, False)])),
                ('bill_schedule', models.ForeignKey(blank=True, to='scheduleapp.BillSchedule', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='billscheduleapprovaldetails',
            name='bill_schedule',
            field=models.ForeignKey(blank=True, to='scheduleapp.BillScheduleDetails', null=True),
        ),
    ]
