import django
from django.db import models
from datetime import date


# Create your models here.
from adminapp.models import City, BillCycle, RouteDetail, UserProfile

IS_DELETED = (
    (True, True),
    (False, False),
)

ROW_STATUS = (
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
)

READING_TAKEN_BY_STATUS = (
    ('Manual', 'Manual'),
    ('QRCode', 'QRCode'),
)


class SimpleCount(models.Model):
    num = models.IntegerField(default=0)

    def __unicode__(self):
        return unicode(self.num)


def checkMonth(month):
    if month > 9:
        return str(month)
    else:
        return '0' + str(month)


class ConsumerDetails(models.Model):
    name = models.CharField(max_length=200, blank=False, null=True)
    consumer_no = models.CharField(max_length=200, blank=False, null=True)
    email_id = models.CharField(max_length=50, blank=False, null=True)
    contact_no = models.CharField(max_length=50, blank=False, null=True)
    address_line_1 = models.CharField(max_length=500, blank=True, null=True)
    address_line_2 = models.CharField(max_length=500, blank=True, null=True)
    address_line_3 = models.CharField(max_length=500, blank=True, null=True)
    village = models.CharField(max_length=500, blank=True, null=True)
    city = models.ForeignKey(City, blank=False, null=True)
    pin_code = models.CharField(max_length=10, blank=True, null=True)
    route = models.ForeignKey(RouteDetail, blank=False, null=True)
    bill_cycle = models.ForeignKey(BillCycle, blank=False, null=True)
    feeder_code = models.CharField(max_length=20, blank=True, null=True)
    feeder_name = models.CharField(max_length=255, blank=True, null=True)

    meter_no = models.CharField(max_length=30, blank=False, null=True)
    dtc = models.CharField(max_length=30, blank=True, null=False)
    dtc_dec = models.CharField(max_length=255, blank=True, null=True)
    pole_no = models.CharField(max_length=30, blank=True, null=True)

    meter_digit = models.CharField(max_length=5, blank=True, null=True)
    connection_status = models.CharField(max_length=100, blank=True, null=True)

    month = models.CharField(max_length=20, blank=False, null=True)
    bill_month = models.CharField(max_length=20, blank=False, null=True)

    lattitude = models.CharField(max_length=50, blank=False, null=True)
    longitude = models.CharField(max_length=50, blank=False, null=True)

    prev_feeder_code = models.CharField(max_length=20, blank=True, null=True)
    prev_reading = models.CharField(max_length=20, blank=True, null=True)
    curr_reading_date = models.DateField(blank=True, null=True)
    prev_reading_date = models.DateField(blank=True, null=True)
    killowatt = models.CharField(max_length=20, blank=True, null=True)
    consumption = models.CharField(max_length=20, blank=True, null=True)
    avg_six_months = models.CharField(max_length=20, blank=True, null=True)


    fath_hus_name = models.CharField(max_length=100, blank=True, null=True)
    cis_division = models.CharField(max_length=100, blank=True, null=True)
    bu = models.CharField(max_length=100, blank=True, null=True)
    account_id = models.CharField(max_length=100, blank=True, null=True)
    mu_no = models.CharField(max_length=100, blank=True, null=True)
    prev_month = models.CharField(max_length=100, blank=True, null=True)
    pn33_bill_month = models.CharField(max_length=100, blank=True, null=True)
    bill_no = models.CharField(max_length=100, blank=True, null=True)
    trf_catg = models.CharField(max_length=100, blank=True, null=True)
    conn_date = models.CharField(max_length=100, blank=True, null=True)
    load_unit_cd = models.CharField(max_length=100, blank=True, null=True)
    duty_cd = models.CharField(max_length=100, blank=True, null=True)
    urban_flg = models.CharField(max_length=100, blank=True, null=True)
    area_cd = models.CharField(max_length=100, blank=True, null=True)
    area_name = models.CharField(max_length=100, blank=True, null=True)
    sequence = models.CharField(max_length=100, blank=True, null=True)
    gr_no = models.CharField(max_length=100, blank=True, null=True)
    rd_no = models.CharField(max_length=100, blank=True, null=True)
    mtr_inst_dt = models.CharField(max_length=100, blank=True, null=True)
    mtr_repl_dt = models.CharField(max_length=100, blank=True, null=True)
    meter_phase = models.CharField(max_length=100, blank=True, null=True)
    make = models.CharField(max_length=100, blank=True, null=True)
    mtr_type = models.CharField(max_length=100, blank=True, null=True)
    mf = models.CharField(max_length=100, blank=True, null=True)
    prev_rtg = models.CharField(max_length=100, blank=True, null=True)
    curr_rtg = models.CharField(max_length=100, blank=True, null=True)
    curr_rtg_stts = models.CharField(max_length=100, blank=True, null=True)
    prev_rtg_stts = models.CharField(max_length=100, blank=True, null=True)
    lcr_unit = models.CharField(max_length=100, blank=True, null=True)


    created_by = models.CharField(max_length=500, blank=False, null=True)
    updated_by = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(choices=IS_DELETED, default=False)
    is_new = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.name)


class UnBilledConsumers(models.Model):
    name = models.CharField(max_length=200, blank=False, null=True)
    bill_cycle_code = models.CharField(max_length=50, blank=False, null=True)
    consumer_no = models.CharField(max_length=50, blank=False, null=True)
    meter_no = models.CharField(max_length=50, blank=False, null=True)
    pole_no = models.CharField(max_length=30, blank=True, null=True)
    route_code = models.CharField(max_length=50, blank=False, null=True)
    current_meter_reading = models.CharField(max_length=20, blank=True, null=True)
    dtc = models.CharField(max_length=500, blank=True, null=False)
    connection_status = models.CharField(max_length=100, blank=True, null=True)
    address_line_1 = models.CharField(max_length=500, blank=True, null=False)
    address_line_2 = models.CharField(max_length=500, blank=True, null=False)
    address_line_3 = models.CharField(max_length=500, blank=True, null=False)
    email_id = models.CharField(max_length=100, blank=True, null=False)
    contact_no = models.CharField(max_length=20, blank=True, null=False)
    meterreader = models.ForeignKey(UserProfile, blank=False, null=True)
    reader_status = models.CharField(max_length=20, blank=True, null=False)
    created_by = models.CharField(max_length=20, blank=True, null=False)
    updated_by = models.CharField(max_length=20, blank=True, null=False)
    reading_date = models.DateTimeField(default=django.utils.timezone.now)
    created_on = models.DateTimeField(default=django.utils.timezone.now)
    updated_on = models.DateTimeField(blank=True, null=True)
    meter_status = models.CharField(max_length=20, blank=True, null=False)
    comment = models.CharField(max_length=200, blank=True, null=False)
    reading_month = models.CharField(max_length=20, blank=False, null=False,
                                     default=str(date.today().year) + checkMonth(date.today().month))
    reading_taken_by = models.CharField(max_length=20,default='Manual',choices= READING_TAKEN_BY_STATUS)
    suspicious_image_url = models.URLField(max_length=500, blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    is_qr_code_tempered = models.BooleanField(default=False)
    qr_code_image_url = models.URLField(max_length=500, blank=True, null=True)
    suspicious_activity = models.BooleanField(default=False)
    suspicious_activity_remark = models.CharField(max_length=200, blank=True, null=False)
    is_confirmed = models.BooleanField(default=False)
    is_descarded = models.BooleanField(default=False)
    is_assigned = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.id)
