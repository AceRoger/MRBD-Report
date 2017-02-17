from django.db import models
from adminapp.models import BillCycle,ApprovalDetails
import django
from datetime import date
# Create your models here.

IS_DELETED = (
    (True, True),
    (False, False),
)

STATUS = (
        ('Not Confirmed', 'Not Confirmed'),
        ('Confirmed', 'Confirmed'),
        ('Pending Approval', 'Pending Approval'),
        ('Rejected', 'Rejected'),
    )

def checkMonth(month):
    if month > 9:
        return str(month)
    else:
        return '0' + str(month)

class BillSchedule(models.Model):
    bill_cycle = models.ForeignKey(BillCycle, blank=True, null=True)
    month = models.CharField(max_length=20, blank=False, null=False, default=str(date.today().year) + checkMonth(date.today().month))
    created_by = models.CharField(max_length=500, blank=False, null=False)
    updated_by = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    is_imported = models.BooleanField(choices=IS_DELETED, default=False)
    is_uploaded = models.BooleanField(choices=IS_DELETED, default=False)
    is_deleted = models.BooleanField(choices=IS_DELETED, default=False)

    def __unicode__(self):
        return unicode(str(self.month) + '-' + str(self.bill_cycle.bill_cycle_code))


class BillScheduleDetails(models.Model):

    STATUS = (
        ('Not Confirmed', 'Not Confirmed'),
        ('Confirmed', 'Confirmed'),
        ('Pending Approval', 'Pending Approval'),
        ('Rejected', 'Rejected'),
    )
    billSchedule = models.ForeignKey(BillSchedule, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    accounting_date = models.DateField(blank=True, null=True)
    estimated_date = models.DateField(blank=True, null=True)
    month = models.CharField(max_length=20, blank=False, null=False,
                             default=str(date.today().year) + checkMonth(date.today().month))
    version = models.CharField(max_length=500, blank=False, null=True, default='0')
    status = models.CharField(max_length=500, default='Not Confirmed',choices=STATUS)
    last_confirmed = models.BooleanField(choices=IS_DELETED, default=False)
    is_original = models.BooleanField(choices=IS_DELETED, default=False)
    is_active = models.BooleanField(choices=IS_DELETED, default=True)
    created_by = models.CharField(max_length=500, blank=False, null=False)
    updated_by = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(choices=IS_DELETED, default=False)

    def __unicode__(self):
        return unicode(str(self.billSchedule) +'-'+str(self.status))

class BillScheduleApprovalDetails(models.Model):
    bill_schedule = models.ForeignKey(BillScheduleDetails, blank=True, null=True)
    approval_details = models.ForeignKey(ApprovalDetails, blank=True, null=True)
    status = models.CharField(max_length=500, default='Pending Approval',choices=STATUS)
    remark = models.CharField(max_length=500, blank=False, null=False)
    send_date = models.DateField(blank=True, null=True)
    approval_date = models.DateField(blank=True, null=True)
    created_by = models.CharField(max_length=500, blank=False, null=False)
    updated_by = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(choices=IS_DELETED, default=False)


    def __unicode__(self):
        return unicode(str(self.bill_schedule) +'-'+ str(self.approval_details) )


class PN33Download(models.Model):
    DOWNLOAD_STATUS=(
        ('Not Started','Not Started'),
        ('Started','Started'),
        ('Failed','Failed'),
        ('Completed','Completed'),
        )
    bill_schedule = models.ForeignKey(BillSchedule, blank=True, null=True)
    month = models.CharField(max_length=20, blank=False, null=False, default=str(date.today().year)+checkMonth(date.today().month))
    start_date = models.DateTimeField(blank=True, null=True, default=None)
    end_date = models.DateTimeField(blank=True, null=True)
    asy_job_id = models.CharField(max_length=100, blank=True, null=True)
    download_status=models.CharField(max_length=500, default='Not Started',choices=DOWNLOAD_STATUS)
    created_by = models.CharField(max_length=500, blank=False, null=False)
    updated_by = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(choices=IS_DELETED,default=False)

    def __unicode__(self):
        return unicode(str(self.month)+'-'+str(self.bill_schedule.bill_cycle.bill_cycle_code))


class UploadB30(models.Model):

    DOWNLOAD_STATUS=(
        ('Not Started','Not Started'),
        ('Started','Started'),
        ('Failed','Failed'),
        ('Completed','Completed'),
        )
    bill_schedule = models.ForeignKey(BillSchedule, blank=True, null=True)
    month = models.CharField(max_length=20, blank=False, null=False, default=str(date.today().year)+checkMonth(date.today().month))
    start_date = models.DateTimeField(blank=True, null=True, default=None)
    end_date = models.DateTimeField(blank=True, null=True)
    asy_job_id = models.CharField(max_length=100, blank=True, null=True)
    status=models.CharField(max_length=500, default='Not Started',choices=DOWNLOAD_STATUS)

    created_by = models.CharField(max_length=500, blank=False, null=False)
    updated_by = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)

    is_deleted = models.BooleanField(choices=IS_DELETED,default=False)

    def __unicode__(self):
        return unicode(str(self.month)+'-'+str(self.bill_schedule.bill_cycle.bill_cycle_code))
