import django
from adminapp.models import UserProfile,BillCycle, RouteDetail
from django.db import models
from django.utils import timezone

IS_DELETED = (
    ('YES', 'YES'),
    ('NO', 'NO'),
)


# class PreferredRoutes(models.Model):
#     # preferred_id = models.AutoField(primary_key=True, editable=False)
#     route = models.ForeignKey(RouteDetail, blank=True, null=True)
#     user = models.ForeignKey(UserProfile, blank=True, null=True)
#     preference_no = models.CharField(max_length=20,blank=True, null=True)
#     is_deleted = models.CharField(max_length=20, default='NO', choices=IS_DELETED)
#     preferredroutes_created_by = models.CharField(max_length=500, blank=True, null=True)
#     preferredroutes_updated_by = models.CharField(max_length=500, blank=True, null=True)
#     preferredroutes_created_date = models.DateTimeField(default=django.utils.timezone.now)
#     preferredroutes_updated_date = models.DateTimeField(blank=True, null=True)
#
#     def __unicode__(self):
#         return unicode(self.user)



class PreferredRoutes(models.Model):
    bill_cycle_code=models.CharField(max_length=255, blank=True, null=True)
    route = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(UserProfile, blank=True, null=True)
    preference_no = models.CharField(max_length=20,blank=True, null=True)
    is_deleted = models.CharField(max_length=20, default='NO', choices=IS_DELETED)
    preferredroutes_created_by = models.CharField(max_length=500, blank=True, null=True)
    preferredroutes_updated_by = models.CharField(max_length=500, blank=True, null=True)
    preferredroutes_created_date = models.DateTimeField(default=django.utils.timezone.now)
    preferredroutes_updated_date = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.user)

class PreferredBillCycle(models.Model):
    user = models.ForeignKey(UserProfile, blank=True, null=True)
    bill_cycle_code = models.CharField(max_length=255, blank=True, null=True)
    preference_no = models.CharField(max_length=20, blank=True, null=True)
    PreferredBillCycle_created_date = models.DateTimeField(default=django.utils.timezone.now)
    PreferredBillCycle_updated_date = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.user)

class DeviceDetail(models.Model):
    # device_id = models.AutoField(primary_key=True)
    company_name=models.CharField(max_length=500,blank=False,null=False)
    device_name = models.CharField(max_length=500,blank=False,null=False)
    make = models.CharField(max_length=500,blank=False,null=False)
    imei_no = models.CharField(max_length=500,blank=False,null=False)
    user_id = models.ForeignKey(UserProfile, blank=True, null=True)
    is_deleted = models.CharField(max_length=20, default='NO', choices=IS_DELETED)
    device_details_created_by = models.CharField(max_length=500, blank=False, null=False)
    device_details_updated_by = models.CharField(max_length=500, blank=True, null=True)
    device_details_created_date = models.DateTimeField(default=django.utils.timezone.now)
    device_details_updated_date = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.company_name)


