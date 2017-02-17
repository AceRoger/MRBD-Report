import django
from django.db import models
from consumerapp.models import ConsumerDetails

from adminapp.models import City, BillCycle, UserProfile, RouteDetail
from consumerapp.models import UnBilledConsumers
from django.contrib.auth.models import User
from datetime import date

ROW_STATUS = (
    ('ACTIVE', 'ACTIVE'),
    ('INACTIVE', 'INACTIVE'),
)

JOBCARD_STATUS = (
    ('ALLOCATED', 'ALLOCATED'),
    ('ASSIGNED', 'ASSIGNED'),
    ('REASSIGNED', 'REASSIGNED'),
    ('COMPLETED', 'COMPLETED'),
    ('DEASSIGNED', 'DEASSIGNED'),
    ('DUPLICATE', 'DUPLICATE'),
    ('REVISIT', 'REVISIT'),
)

METER_STATUS = (
    ('Normal', 'Normal'),
    ('Faulty', 'Faulty'),
    ('LockPremise', 'LockPremise'),
    ('ReadingOverflow', 'ReadingOverflow'),
    ('MeterChange', 'MeterChange'),
    ('Inaccessible', 'Inaccessible'),
    ('MeterMissing', 'MeterMissing'),
    ('ReadingNotTaken', 'ReadingNotTaken'),
)

READER_STATUS = (
    ('Normal', 'Normal'),
    ('Mechanical', 'Mechanical'),
    ('Disconnected', 'Disconnected'),
    ('Shifting', 'Shifting'),
    ('MeterChanged', 'MeterChanged'),
    ('ReadingOverflow', 'ReadingOverflow'),
)

READING_TAKEN_BY_STATUS = (
    ('Manual', 'Manual'),
    ('QRCode', 'QRCode'),
)

READING_STATUS = (
    ('validation1', 'validation1'),
    ('validation2', 'validation2'),
    ('complete', 'complete'),
    ('revisit', 'revisit'),
)

IS_DELETED = (
    (True, True),
    (False, False),
)


def checkMonth(month):
    if month > 9:
        return str(month)
    else:
        return '0' + str(month)


class RouteAssignment(models.Model):
    DISPATCH_STATUS = (
        ('NOT_DISPATCHED', 'Not Dispatched'),
        ('DISPATCHED', 'Dispatched'),
        ('STARTED', 'Started'),
    )
    routedetail = models.ForeignKey(RouteDetail, blank=True, null=True)
    meterreader = models.ForeignKey(UserProfile, blank=True, null=True)
    assign_date = models.DateTimeField(default=django.utils.timezone.now, blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    reading_month = models.CharField(max_length=20, blank=False, null=False, default=str(date.today().year) + checkMonth(date.today().month))
    is_deleted = models.BooleanField(default=False)
    record_status = models.CharField(max_length=10, default='Active', choices=ROW_STATUS)
    dispatch_status = models.CharField(max_length=20,default='Not Dispatched',blank=True,null=True)
    is_active = models.BooleanField(default=False) # if false means yet to dispatched
    sent_to_mr = models.BooleanField(default=False) # is it sent to mr
    is_reading_completed = models.BooleanField(default=False)#reading status for route complete or incomplete
    created_by = models.CharField(max_length=50, blank=False, null=False)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    created_on = models.DateTimeField(default=django.utils.timezone.now)
    updated_on = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.routedetail)


class RouteProcess(models.Model):
    routedetail = models.ForeignKey(RouteDetail, blank=True, null=True)
    reading_month = models.CharField(max_length=20, blank=True, null=True, default=str(date.today().year) + checkMonth(date.today().month))
    is_processing = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.routedetail)

class RouteDeassigned(models.Model):
    routedetail = models.ForeignKey(RouteDetail, blank=True, null=True)
    meterreader = models.ForeignKey(UserProfile, blank=True, null=True)
    deassign_date = models.DateTimeField(default=django.utils.timezone.now, blank=True, null=True)


class JobCard(models.Model):
    routeassigned = models.ForeignKey(RouteAssignment, blank=False, null=True)
    consumerdetail = models.ForeignKey(ConsumerDetails, blank=False, null=True)
    meterreader = models.ForeignKey(UserProfile, blank=False, null=True)
    assigned_date = models.DateTimeField(default=django.utils.timezone.now,blank=True, null=True)
    record_status = models.CharField(max_length=20,default='ALLOCATED',choices= JOBCARD_STATUS)
    completion_date = models.DateTimeField(blank=True, null=True)
    #job_type = models.CharField(max_length=100, blank=True, null=True)
    reading_month = models.CharField(max_length=20, blank=False, null=False, default=str(date.today().year) + checkMonth(date.today().month))
    is_active = models.BooleanField(default=True) # if that record is active, manage this flag in revisit case
    is_deleted = models.BooleanField(default=False) # is nothing but killed, that rec. is ressigned
    is_deleted_for_mr = models.BooleanField(default=False) # is nothing but deassigned/reassigned for that mr
    is_reading_completed = models.BooleanField(default=False)
    is_revisit = models.BooleanField(default=False)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    created_on = models.DateTimeField(default=django.utils.timezone.now)
    Updated_on = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.consumerdetail)


class MeterStatus(models.Model):
    meter_status = models.CharField(max_length=20, blank=True, null=True, default='Normal', choices=METER_STATUS)
    status_code = models.CharField(max_length=20, blank=True, null=True)
    is_deleted = models.BooleanField(choices=IS_DELETED, default=False)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    created_on = models.DateTimeField(default=django.utils.timezone.now)
    Updated_on = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.meter_status)


class ReaderStatus(models.Model):
    reader_status = models.CharField(max_length=20, blank=True, null=True, default= 'Normal', choices=READER_STATUS)
    status_code = models.CharField(max_length=20, blank=True, null=True)
    is_deleted = models.BooleanField(choices=IS_DELETED, default=False)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    created_on = models.DateTimeField(default=django.utils.timezone.now)
    Updated_on = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.reader_status)


class MeterReading(models.Model):
    jobcard = models.ForeignKey(JobCard,blank=False,null=True)
    current_meter_reading = models.CharField(max_length=20,blank=True, null=True)
    image_url= models.URLField(max_length=500, blank=True, null=True)
    meter_status = models.ForeignKey(MeterStatus,blank=False,null=True)
    reader_status = models.ForeignKey(ReaderStatus,blank=False,null=True)
    reading_status = models.CharField(max_length=20,blank=True, null=True,default = 'validation1',choices = READING_STATUS)
    is_assigned_to_v1 = models.BooleanField(default=False)
    is_assigned_to_v2 = models.BooleanField(default=False)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    is_qr_code_tempered = models.BooleanField(default=False)
    qr_code_image_url = models.URLField(max_length=500, blank=True, null=True)
    reading_month = models.CharField(max_length=20, blank=False, null=False, default=str(date.today().year) + checkMonth(date.today().month))
    reading_date=models.DateTimeField(default=django.utils.timezone.now,blank=True, null=True)
    suspicious_activity = models.BooleanField(default=False)
    suspicious_image_url = models.URLField(max_length=500, blank = True, null=True)
    suspicious_activity_remark = models.CharField(max_length=500, blank=True, null=True)
    comment = models.CharField(max_length=500, blank=True, null=True)
    reading_taken_by = models.CharField(max_length=20,default='Manual',choices= READING_TAKEN_BY_STATUS)
    is_duplicate = models.BooleanField(choices=IS_DELETED,default=False)
    is_active = models.BooleanField(choices=IS_DELETED,default=True)
    is_deleted = models.BooleanField(choices=IS_DELETED,default=False)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    created_on = models.DateTimeField(default=django.utils.timezone.now)
    Updated_on = models.DateTimeField(blank=True, null=True)

    meter_status_v1 = models.ForeignKey(MeterStatus,blank=True,null=True, related_name='meter_status_v1')
    reader_status_v1 = models.ForeignKey(ReaderStatus,blank=True,null=True, related_name='reader_status_v1')
    comment_v1 = models.CharField(max_length=500, blank=True, null=True)
    current_meter_reading_v1 = models.CharField(max_length=20,blank=True, null=True)
    image_remark_v1 = models.CharField(max_length=50,blank=True, null=True, default='')
    updated_by_v1 = models.ForeignKey(UserProfile, blank=True, null=True, related_name='v1')
    validated_on_v1 = models.DateTimeField(blank=True, null=True)

    meter_status_v2 = models.ForeignKey(MeterStatus,blank=True,null=True, related_name='meter_status_v2')
    reader_status_v2 = models.ForeignKey(ReaderStatus,blank=True,null=True, related_name='reader_status_v2')
    comment_v2 = models.CharField(max_length=500, blank=True, null=True)
    current_meter_reading_v2 = models.CharField(max_length=20,blank=True, null=True)
    image_remark_v2 = models.CharField(max_length=50,blank=True, null=True , default='')
    updated_by_v2 = models.ForeignKey(UserProfile, blank=True, null=True, related_name='v2')
    validated_on_v2 = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.jobcard)


class ValidatorAssignment(models.Model):
    user = models.ForeignKey(UserProfile, blank=False, null=True, related_name='user')
    # meterreader = models.ForeignKey(UserProfile, blank=False, null=True, related_name='meterreader')
    meterreading = models.ForeignKey(MeterReading, blank=False, null=True)
    remark = models.CharField(max_length=200, blank=True, null=True)
    result = models.CharField(max_length=200, blank=True, null=True)
    reading_month = models.CharField(max_length=20, blank=False, null=False, default=str(date.today().year) + checkMonth(date.today().month))
    assigned_to = models.CharField(max_length=20, blank=True, null=True) # validator1 OR validator2
    created_by = models.CharField(max_length=50, blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    created_on = models.DateTimeField(default=django.utils.timezone.now)
    Updated_on = models.DateTimeField(blank=True, null=True)
    is_validated = models.BooleanField(default=False)  # already validated
    sent_to_revisit = models.BooleanField(default=False)  # if send to revisit


class ValidatorAssignmentCount(models.Model):
    user = models.ForeignKey(UserProfile, blank=False, null=True)
    reading_month = models.CharField(max_length=20, blank=False, null=False, default=str(date.today().year) + checkMonth(date.today().month))
    count = models.IntegerField(blank=True, null=True)


class UnbilledConsumerAssignment(models.Model):
    user = models.ForeignKey(UserProfile, blank=False, null=True, related_name='unbilleduser')
    unbillconsumer =models.ForeignKey(UnBilledConsumers, blank=True, null = True)
    reading_month = models.CharField(max_length=20, blank=False, null=False, default=str(date.today().year) + checkMonth(date.today().month))
    created_by = models.CharField(max_length=50, blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    created_on = models.DateTimeField(default=django.utils.timezone.now)
    Updated_on = models.DateTimeField(blank=True, null=True)
    is_confirmed =  models.BooleanField(default=False)  # is confirmed or not

class UnbilledConsumerAssignmentCount(models.Model):
    user = models.ForeignKey(UserProfile, blank=False, null=True)
    count = models.IntegerField(blank=True, null=True)


#
# class ImageStorageMeta(models.model):
#     image_url=models.URLField(max_length=500,blank=False)
#     meterreading=models.ForeignKey(MeterReading,blank=False,null=True)
