import datetime
from adminapp.models import RouteDetail, RT_DETAILS
from consumerapp.models import ConsumerDetails
from adminapp import constraints

__author__ = 'vkm chandel'

from django import template
from scheduleapp.models import BillSchedule, PN33Download, BillScheduleDetails

register = template.Library()

MONTHS = {
    '01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR',
    '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AUG',
    '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'}


@register.filter
def startDate(pn33download):
    try:
        print 'pn33download',pn33download
        print 'pn33download.bill_schedule',pn33download.bill_schedule
        billScheduleDetails = BillScheduleDetails.objects.get(billSchedule=pn33download.bill_schedule,
                                                              last_confirmed=True)
        return billScheduleDetails.start_date
    except Exception, e:
        print 'Exception|customfilter|startDate', e
        return None


@register.filter
def endDate(pn33download):
    try:
        billScheduleDetails = BillScheduleDetails.objects.get(billSchedule=pn33download.bill_schedule,
                                                              last_confirmed=True)
        return billScheduleDetails.end_date
    except Exception, e:
        print 'Exception|customfilter|endDate', e
        return None

@register.filter
def getTotalRoute(pn33download):
    try:
        totalRoute = RouteDetail.objects.filter(billcycle=pn33download.bill_schedule.bill_cycle,
                                                              is_deleted=False,bill_month=pn33download.month).count()
        return totalRoute
    except Exception, e:
        print 'Exception|customfilter|getTotalRoute', e
        return None


@register.filter
def getTotalConsumer(pn33download):
    try:
        totalConsumer = ConsumerDetails.objects.filter(bill_cycle=pn33download.bill_schedule.bill_cycle,
                                                              is_deleted=False,bill_month=pn33download.month).count()
        return totalConsumer
    except Exception, e:
        print 'Exception|customfilter|getTotalConsumer', e
        return None


@register.filter
def getPercentage(pn33download):
    try:
        print 'pn33download.bill_schedule.bill_cycle',pn33download.bill_schedule.bill_cycle
        print 'pn33download.month',pn33download.month

        billCycle_obj=pn33download.bill_schedule.bill_cycle
        rt_detiails_count=RT_DETAILS.objects.filter(BILL_CYC_CD=billCycle_obj.bill_cycle_code,CURR_MONTH=constraints.month_minus(pn33download.month)).count()
        consumerDetails_count=ConsumerDetails.objects.filter(bill_cycle=billCycle_obj,bill_month=pn33download.month).count()

        percentage= float(consumerDetails_count)/float(rt_detiails_count)*100
        print 'percentage===>',percentage
        return round(percentage,2)
    except Exception, e:
        print 'Exception|customfilter|getPercentage', e
        return '0.0'


@register.filter
def getTimeDuration(pn33download):
    try:
        print 'pn33download.bill_schedule.bill_cycle',pn33download.bill_schedule.bill_cycle
        print 'pn33download.month',pn33download.month

        currentTime=datetime.datetime.now()
        starttime=pn33download.start_date

        print 'currentTime',currentTime
        print 'starttime',starttime
        starttime = starttime.replace(tzinfo=None)
        duration=currentTime-starttime
        print 'duration',duration
        result=divmod(duration.days * 86400 + duration.seconds, 60)
        result=str(result[0])+':'+str(result[1])
        return result
    except Exception, e:
        print 'Exception|customfilter|getTimeDuration', e
        return None


@register.filter
def get_month(yearMonth):
    try:
        print "=================Months==============",MONTHS[yearMonth[-2:]]
        return str(MONTHS[yearMonth[-2:]])+' '+str(yearMonth[:-2])
    except Exception, e:
        print 'Exception|billCycleFilter|month', e
        return None