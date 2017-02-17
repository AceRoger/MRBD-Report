import django
from django.db import models
from django.contrib.auth.models import User
from datetime import date

IS_DELETED = (
    (True, True),
    (False, False),
)

ROLE_STATUS = (
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
)


# Create your models here.

def checkMonth(month):
    if month > 9:
        return str(month)
    else:
        return '0' + str(month)


class Utility(models.Model):
    utility = models.CharField(max_length=100, blank=False, null=False)
    created_by = models.CharField(max_length=500, blank=False, null=False)
    updated_by = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(choices=IS_DELETED, default=False)

    def __unicode__(self):
        return unicode(self.utility)


class BillCycle(models.Model):
    bill_cycle_code = models.CharField(max_length=100, blank=False, null=False)
    zone = models.ForeignKey('Zone', blank=True, null=True)
    area = models.ForeignKey('Area', blank=True, null=True)
    bill_cycle_name = models.CharField(max_length=100, blank=False, null=True)
    city = models.ForeignKey('City', blank=True, null=True)
    utility = models.ForeignKey('Utility', blank=True, null=True)
    created_by = models.CharField(max_length=500, blank=False, null=False)
    updated_by = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(choices=IS_DELETED, default=False)

    def __unicode__(self):
        return unicode(self.bill_cycle_code)


class Zone(models.Model):
    zone_name = models.CharField(max_length=250, blank=False, null=False)
    created_by = models.CharField(max_length=500, blank=False, null=True)
    updated_by = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(choices=IS_DELETED, default=False)

    def __unicode__(self):
        return unicode(self.zone_name)

class Area(models.Model):
    area_name = models.CharField(max_length=250, blank=False, null=False)
    created_by = models.CharField(max_length=500, blank=False, null=True)
    updated_by = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(choices=IS_DELETED, default=False)

    def __unicode__(self):
        return unicode(self.area_name)

class RouteDetail(models.Model):
    route_code = models.CharField(max_length=500, blank=False, null=False)
    billcycle = models.ForeignKey(BillCycle, blank=True, null=True)
    month = models.CharField(max_length=20, blank=False, null=False)
    bill_month = models.CharField(max_length=20, blank=False, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    created_on = models.DateTimeField(default=django.utils.timezone.now)
    updated_on = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(choices=IS_DELETED, default=False)

    def __unicode__(self):
        return unicode(self.route_code)


class UserPrivilege(models.Model):
    privilege = models.CharField(max_length=500, blank=False, null=False)
    parent = models.ForeignKey('self', blank=True, null=True)
    created_by = models.CharField(max_length=500, blank=False, null=False)
    updated_by = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(choices=IS_DELETED, default=False)

    def __unicode__(self):
        return unicode(self.privilege)


class UserRole(models.Model):
    role = models.CharField(max_length=500, blank=False, null=False)
    description = models.CharField(max_length=500, blank=True, null=True)
    privilege = models.ManyToManyField(UserPrivilege)
    status = models.CharField(max_length=20, default='Active', choices=ROLE_STATUS)
    created_by = models.CharField(max_length=500, blank=False, null=False)
    updated_by = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(choices=IS_DELETED, default=False)

    def __unicode__(self):
        return unicode(self.role)


class State(models.Model):
    state = models.CharField(max_length=500, blank=True)
    created_by = models.CharField(max_length=500, blank=True, null=True)
    updated_by = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(choices=IS_DELETED, default=False)

    def __unicode__(self):
        return unicode(self.state)


class City(models.Model):
    city = models.CharField(max_length=500, default=None)
    state = models.ForeignKey(State, blank=True, null=True)
    created_by = models.CharField(max_length=500, blank=True, null=True)
    updated_by = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(choices=IS_DELETED, default=False)

    def __unicode__(self):
        return unicode(self.city)


class EmployeeType(models.Model):
    employee_type = models.CharField(max_length=500, blank=False, null=False)
    created_by = models.CharField(max_length=500, blank=False, null=False)
    updated_by = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(choices=IS_DELETED, default=False)

    def __unicode__(self):
        return unicode(self.employee_type)


class UserProfile(User):
    USER_STATUS = (
        ('ACTIVE', 'ACTIVE'),
        ('INACTIVE', 'INACTIVE'),
    )

    USER_TYPE = (
        ('WEB_USER', 'WEB_USER'),
        ('METER_READER', 'METER_READER'),
        ('VALIDATOR_1', 'VALIDATOR_1'),
        ('VALIDATOR_2', 'VALIDATOR_2'),
        ('APPROVAL', 'APPROVAL'),
    )

    contact_no = models.CharField(max_length=15, blank=False, null=False)
    address_line_1 = models.CharField(max_length=500, blank=True, null=False)
    address_line_2 = models.CharField(max_length=500, blank=True, null=False)
    city = models.ForeignKey(City, blank=False, null=True)
    state = models.ForeignKey(State, blank=False, null=True)
    pincode = models.CharField(max_length=500, blank=True, null=False)
    role = models.ForeignKey(UserRole, blank=True, null=True)
    employee_id = models.CharField(max_length=100, blank=True, null=False)
    employee_type = models.ForeignKey(EmployeeType, blank=True, null=True)
    type = models.CharField(max_length=20, default='WEB_USER', choices=USER_TYPE)
    status = models.CharField(max_length=20, default='ACTIVE', choices=USER_STATUS)
    created_by = models.CharField(max_length=500, blank=False, null=False)
    updated_by = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(default=django.utils.timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(choices=IS_DELETED, default=False)

    def __unicode__(self):
        return unicode(str(self.username)+'-'+str(self.type))


class ApprovalDetails(models.Model):

    approval = models.ForeignKey(UserProfile, blank=False, null=True, related_name='approvals')
    days = models.CharField(max_length=15, blank=False, null=False,unique=True)
    is_deleted = models.BooleanField(choices=IS_DELETED, default=False)
    def __unicode__(self):
        return unicode(str(self.approval)+ '-' +str(self.days))


class Availability(models.Model):
    availability = (
        ('AVAILABLE', 'AVAILABLE'),
        ('NOT_AVAILABLE', 'NOT_AVAILABLE'),
    )
    available = models.CharField(max_length=15, blank=False, null=False,choices=availability)
    start_date = models.DateField(blank=True, null=True, default=None)
    end_date = models.DateField(blank=True, null=True)
    validator = models.ForeignKey(UserProfile, blank=False, null=True, related_name='validator')

    def __unicode__(self):
        return unicode(str(self.id)+str(self.available)+str(self.validator))


class RT_MASTER(models.Model):
    CIS_DIVISION = models.CharField(max_length=20, blank=True, null=True)
    BILL_MONTH = models.CharField(max_length=20, blank=True, null=True)
    BILL_CYC_CD = models.CharField(max_length=20, blank=True, null=True)
    ROUTE_ID = models.CharField(max_length=20, blank=True, null=True)
    INSERTEDON = models.DateTimeField(default=django.utils.timezone.now)

    def __unicode__(self):
        return unicode(str(self.ROUTE_ID) + '-' + str(self.BILL_MONTH))

    class Meta:
        db_table = 'RT_MASTER'


class RT_DETAILS(models.Model):
    ID = models.AutoField(primary_key=True, max_length=10)
    CIS_DIVISION = models.CharField(max_length=254, blank=True, null=True)
    BILL_CYC_CD = models.CharField(max_length=254, blank=True, null=True)
    BU = models.CharField(max_length=254, blank=True, null=True)
    PC = models.CharField(max_length=254, blank=True, null=True)
    CONS_NO = models.CharField(max_length=254, blank=True, null=True)
    ACCOUNT_ID = models.CharField(max_length=254, blank=True, null=True)
    MU_NO = models.CharField(max_length=254, blank=True, null=True)
    CONS_NAME = models.CharField(max_length=254, blank=True, null=True)
    FATH_HUS_NAME = models.CharField(max_length=254, blank=True, null=True)
    ADD1 = models.CharField(max_length=254, blank=True, null=True)
    ADD2 = models.CharField(max_length=254, blank=True, null=True)
    ADD3 = models.CharField(max_length=254, blank=True, null=True)
    VILLAGE = models.CharField(max_length=254, blank=True, null=True)
    PREV_MONTH = models.CharField(max_length=254, blank=True, null=True)
    BILL_MONTH = models.CharField(max_length=254, blank=True, null=True)
    CURR_MONTH = models.CharField(max_length=254, blank=True, null=True)
    BILL_NO = models.CharField(max_length=254, blank=True, null=True)
    TRF_CATG = models.CharField(max_length=254, blank=True, null=True)
    CONN_DATE = models.CharField(max_length=254, blank=True, null=True)
    CONS_STATUS = models.CharField(max_length=254, blank=True, null=True)
    LOAD = models.CharField(max_length=20, blank=True, null=True)
    LOAD_UNIT_CD = models.CharField(max_length=254, blank=True, null=True)
    DUTY_CD = models.CharField(max_length=254, blank=True, null=True)
    URBAN_FLG = models.CharField(max_length=254, blank=True, null=True)
    FEEDER_CD = models.CharField(max_length=254, blank=True, null=True)
    FEEDER_NAME = models.CharField(max_length=254, blank=True, null=True)
    DTC_CD = models.CharField(max_length=254, blank=True, null=True)
    DTC_DESC = models.CharField(max_length=500, blank=True, null=True)
    AREA_CD = models.CharField(max_length=254, blank=True, null=True)
    AREA_NAME = models.CharField(max_length=254, blank=True, null=True)
    ROUTE = models.CharField(max_length=254, blank=True, null=True)
    SEQUENCE = models.CharField(max_length=254, blank=True, null=True)
    GR_NO = models.CharField(max_length=254, blank=True, null=True)
    RD_NO = models.CharField(max_length=254, blank=True, null=True)
    POLE_NO = models.CharField(max_length=254, blank=True, null=True)
    METER_NO = models.CharField(max_length=254, blank=True, null=True)
    MTR_INST_DT = models.DateField(blank=True, null=True)
    MTR_REPL_DT = models.DateField(blank=True, null=True)
    METER_PHASE = models.CharField(max_length=254, blank=True, null=True)
    MAKE = models.CharField(max_length=254, blank=True, null=True)
    METER_DIGIT = models.CharField(max_length=254, blank=True, null=True)
    MTR_TYPE = models.CharField(max_length=254, blank=True, null=True)
    MF = models.CharField(max_length=254, blank=True, null=True)
    PREVIOUS_RTG_DT = models.DateField(blank=True, null=True)
    CURRENT_RTG_DT = models.DateField(blank=True, null=True)
    PREV_RTG = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    CURR_RTG = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    CURR_RTG_STTS = models.CharField(max_length=254, blank=True, null=True)
    PREV_RTG_STTS = models.CharField(max_length=254, blank=True, null=True)
    AVG = models.CharField(max_length=254, blank=True, null=True)
    LCR_UNIT = models.CharField(max_length=254, blank=True, null=True)
    LATTITUDE = models.CharField(max_length=254, blank=True, null=True)
    LONITUDE = models.CharField(max_length=254, blank=True, null=True)

    def __unicode__(self):
        return unicode(str(self.VILLAGE) + '-' + str(self.BILL_MONTH))

    class Meta:
        db_table = 'RT_DETAILS'


class UPLD_MTR_RDNG(models.Model):
    BILL_CYC = models.CharField(max_length=254, blank=True, null=True)
    BILL_MONTH = models.CharField(max_length=254, blank=True, null=True)
    CUSTOMER_ID = models.CharField(max_length=254, blank=True, null=True)
    DOCUMENT_TYPE = models.CharField(max_length=254, blank=True, null=True)
    DTR_NO = models.IntegerField(blank=True, null=True)
    ESTIMATED = models.CharField(max_length=254, blank=True, null=True)
    FEEDER_CODE = models.CharField(max_length=254, blank=True, null=True)
    IMAGE_PATH = models.CharField(max_length=254, blank=True, null=True)
    INSERTEDON = models.DateTimeField(default=django.utils.timezone.now)
    LATTITUDE = models.CharField(max_length=254, blank=True, null=True)
    LONGITUDE = models.CharField(max_length=254, blank=True, null=True)
    MDI = models.CharField(max_length=254, blank=True, null=True)
    METER_READING = models.CharField(max_length=254, blank=True, null=True)
    METER_STATUS = models.CharField(max_length=254, blank=True, null=True)
    PC = models.CharField(max_length=254, blank=True, null=True)
    PF = models.CharField(max_length=254, blank=True, null=True)
    READER_ID = models.CharField(max_length=254, blank=True, null=True)
    READING_DATE = models.CharField(max_length=254, blank=True, null=True)
    ROUTE = models.CharField(max_length=254, blank=True, null=True)
    SEQUENCE = models.CharField(max_length=254, blank=True, null=True)


    def __unicode__(self):
        return unicode(str(self.BILL_MONTH) + '-' + str(self.CUSTOMER_ID))

    class Meta:
        db_table = 'UPLD_MTR_RDNG'

