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
            name='ConsumerDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, null=True)),
                ('consumer_no', models.CharField(max_length=200, null=True)),
                ('email_id', models.CharField(max_length=50, null=True)),
                ('contact_no', models.CharField(max_length=50, null=True)),
                ('address_line_1', models.CharField(max_length=500, null=True, blank=True)),
                ('address_line_2', models.CharField(max_length=500, null=True, blank=True)),
                ('address_line_3', models.CharField(max_length=500, null=True, blank=True)),
                ('village', models.CharField(max_length=500, null=True, blank=True)),
                ('pin_code', models.CharField(max_length=10, null=True, blank=True)),
                ('feeder_code', models.CharField(max_length=20, null=True, blank=True)),
                ('feeder_name', models.CharField(max_length=255, null=True, blank=True)),
                ('meter_no', models.CharField(max_length=30, null=True)),
                ('dtc', models.CharField(max_length=30, blank=True)),
                ('dtc_dec', models.CharField(max_length=255, null=True, blank=True)),
                ('pole_no', models.CharField(max_length=30, null=True, blank=True)),
                ('meter_digit', models.CharField(max_length=5, null=True, blank=True)),
                ('connection_status', models.CharField(max_length=100, null=True, blank=True)),
                ('month', models.CharField(max_length=20, null=True)),
                ('bill_month', models.CharField(max_length=20, null=True)),
                ('lattitude', models.CharField(max_length=50, null=True)),
                ('longitude', models.CharField(max_length=50, null=True)),
                ('prev_feeder_code', models.CharField(max_length=20, null=True, blank=True)),
                ('prev_reading', models.CharField(max_length=20, null=True, blank=True)),
                ('curr_reading_date', models.DateField(null=True, blank=True)),
                ('prev_reading_date', models.DateField(null=True, blank=True)),
                ('killowatt', models.CharField(max_length=20, null=True, blank=True)),
                ('consumption', models.CharField(max_length=20, null=True, blank=True)),
                ('avg_six_months', models.CharField(max_length=20, null=True, blank=True)),
                ('fath_hus_name', models.CharField(max_length=100, null=True, blank=True)),
                ('cis_division', models.CharField(max_length=100, null=True, blank=True)),
                ('bu', models.CharField(max_length=100, null=True, blank=True)),
                ('account_id', models.CharField(max_length=100, null=True, blank=True)),
                ('mu_no', models.CharField(max_length=100, null=True, blank=True)),
                ('prev_month', models.CharField(max_length=100, null=True, blank=True)),
                ('pn33_bill_month', models.CharField(max_length=100, null=True, blank=True)),
                ('bill_no', models.CharField(max_length=100, null=True, blank=True)),
                ('trf_catg', models.CharField(max_length=100, null=True, blank=True)),
                ('conn_date', models.CharField(max_length=100, null=True, blank=True)),
                ('load_unit_cd', models.CharField(max_length=100, null=True, blank=True)),
                ('duty_cd', models.CharField(max_length=100, null=True, blank=True)),
                ('urban_flg', models.CharField(max_length=100, null=True, blank=True)),
                ('area_cd', models.CharField(max_length=100, null=True, blank=True)),
                ('area_name', models.CharField(max_length=100, null=True, blank=True)),
                ('sequence', models.CharField(max_length=100, null=True, blank=True)),
                ('gr_no', models.CharField(max_length=100, null=True, blank=True)),
                ('rd_no', models.CharField(max_length=100, null=True, blank=True)),
                ('mtr_inst_dt', models.CharField(max_length=100, null=True, blank=True)),
                ('mtr_repl_dt', models.CharField(max_length=100, null=True, blank=True)),
                ('meter_phase', models.CharField(max_length=100, null=True, blank=True)),
                ('make', models.CharField(max_length=100, null=True, blank=True)),
                ('mtr_type', models.CharField(max_length=100, null=True, blank=True)),
                ('mf', models.CharField(max_length=100, null=True, blank=True)),
                ('prev_rtg', models.CharField(max_length=100, null=True, blank=True)),
                ('curr_rtg', models.CharField(max_length=100, null=True, blank=True)),
                ('curr_rtg_stts', models.CharField(max_length=100, null=True, blank=True)),
                ('prev_rtg_stts', models.CharField(max_length=100, null=True, blank=True)),
                ('lcr_unit', models.CharField(max_length=100, null=True, blank=True)),
                ('created_by', models.CharField(max_length=500, null=True)),
                ('updated_by', models.CharField(max_length=500, null=True, blank=True)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_date', models.DateTimeField(null=True, blank=True)),
                ('is_deleted', models.BooleanField(default=False, choices=[(True, True), (False, False)])),
                ('is_new', models.BooleanField(default=False)),
                ('bill_cycle', models.ForeignKey(to='adminapp.BillCycle', null=True)),
                ('city', models.ForeignKey(to='adminapp.City', null=True)),
                ('route', models.ForeignKey(to='adminapp.RouteDetail', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SimpleCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('num', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='UnBilledConsumers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, null=True)),
                ('bill_cycle_code', models.CharField(max_length=50, null=True)),
                ('consumer_no', models.CharField(max_length=50, null=True)),
                ('meter_no', models.CharField(max_length=50, null=True)),
                ('pole_no', models.CharField(max_length=30, null=True, blank=True)),
                ('route_code', models.CharField(max_length=50, null=True)),
                ('current_meter_reading', models.CharField(max_length=20, null=True, blank=True)),
                ('dtc', models.CharField(max_length=500, blank=True)),
                ('connection_status', models.CharField(max_length=100, null=True, blank=True)),
                ('address_line_1', models.CharField(max_length=500, blank=True)),
                ('address_line_2', models.CharField(max_length=500, blank=True)),
                ('address_line_3', models.CharField(max_length=500, blank=True)),
                ('email_id', models.CharField(max_length=100, blank=True)),
                ('contact_no', models.CharField(max_length=20, blank=True)),
                ('reader_status', models.CharField(max_length=20, blank=True)),
                ('created_by', models.CharField(max_length=20, blank=True)),
                ('updated_by', models.CharField(max_length=20, blank=True)),
                ('reading_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_on', models.DateTimeField(null=True, blank=True)),
                ('meter_status', models.CharField(max_length=20, blank=True)),
                ('comment', models.CharField(max_length=200, blank=True)),
                ('reading_month', models.CharField(default=b'201611', max_length=20)),
                ('reading_taken_by', models.CharField(default=b'Manual', max_length=20, choices=[(b'Manual', b'Manual'), (b'QRCode', b'QRCode')])),
                ('suspicious_image_url', models.URLField(max_length=500, null=True, blank=True)),
                ('image_url', models.URLField(max_length=500, null=True, blank=True)),
                ('longitude', models.CharField(max_length=20, null=True, blank=True)),
                ('latitude', models.CharField(max_length=20, null=True, blank=True)),
                ('is_qr_code_tempered', models.BooleanField(default=False)),
                ('qr_code_image_url', models.URLField(max_length=500, null=True, blank=True)),
                ('suspicious_activity', models.BooleanField(default=False)),
                ('suspicious_activity_remark', models.CharField(max_length=200, blank=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('is_descarded', models.BooleanField(default=False)),
                ('is_assigned', models.BooleanField(default=False)),
                ('meterreader', models.ForeignKey(to='adminapp.UserProfile', null=True)),
            ],
        ),
    ]
