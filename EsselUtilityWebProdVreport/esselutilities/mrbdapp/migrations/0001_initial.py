# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MeterImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('meter_image', models.ImageField(upload_to=b'meter_reading')),
            ],
        ),
        migrations.CreateModel(
            name='QrTemperedImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('qr_tempered_image', models.ImageField(upload_to=b'qr_tempered')),
            ],
        ),
        migrations.CreateModel(
            name='SuspiciousActivityImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('suspicious_activity_image', models.ImageField(upload_to=b'suspicious_activity')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfileImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('profile_image', models.ImageField(upload_to=b'user_profile')),
            ],
        ),
    ]
