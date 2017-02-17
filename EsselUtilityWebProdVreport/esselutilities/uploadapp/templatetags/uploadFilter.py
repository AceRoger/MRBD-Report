import datetime
from adminapp import constraints
from adminapp.models import RouteDetail, RT_DETAILS
from consumerapp.models import ConsumerDetails
from dispatch.models import MeterReading

__author__ = 'vkm chandel'

from django import template
from scheduleapp.models import BillSchedule, PN33Download, BillScheduleDetails

register = template.Library()


@register.filter
def startDate(uploadB30):
    try:
        billScheduleDetails = BillScheduleDetails.objects.get(billSchedule=uploadB30.bill_schedule,
                                                              last_confirmed=True)
        return billScheduleDetails.start_date
    except Exception, e:
        print 'Exception|uploadfilter|get_startDate', e
        return None


@register.filter
def endDate(uploadB30):
    try:
        billScheduleDetails = BillScheduleDetails.objects.get(billSchedule=uploadB30.bill_schedule,
                                                              last_confirmed=True)
        return billScheduleDetails.end_date
    except Exception, e:
        print 'Exception|uploadfilter|endDate', e
        return None

@register.filter
def getTotalRoute(uploadB30):
    try:
        totalRoute = RouteDetail.objects.filter(billcycle=uploadB30.bill_schedule.bill_cycle,
                                                              is_deleted=False,month=constraints.month_minus(uploadB30.month)).count()
        return totalRoute
    except Exception, e:
        print 'Exception|uploadfilter|getTotalRoute', e
        return None


@register.filter
def getTotalConsumer(uploadB30):
    try:
        totalConsumer = ConsumerDetails.objects.filter(bill_cycle=uploadB30.bill_schedule.bill_cycle,
                                                              is_deleted=False,month=constraints.month_minus(uploadB30.month)).count()
        return totalConsumer
    except Exception, e:
        print 'Exception|uploadfilter|getTotalConsumer', e
        return None


@register.filter
def getTotalReading(uploadB30):
    try:
        bill_cycle=uploadB30.bill_schedule.bill_cycle
        totalMeterReading=MeterReading.objects.filter(jobcard__consumerdetail__bill_cycle=bill_cycle,reading_status='complete',reading_month=uploadB30.month).count()
        return int(totalMeterReading)
    except Exception, e:
        print 'Exception|uploadfilter|getTotalConsumer', e
        return 0



# @register.filter
# def getPercentage(pn33download):
#     try:
#         print 'pn33download.bill_schedule.bill_cycle',pn33download.bill_schedule.bill_cycle
#         print 'pn33download.month',pn33download.month
#
#         billCycle_obj=pn33download.bill_schedule.bill_cycle
#         rt_detiails_count=RT_DETAILS.objects.filter(BILL_CYC_CD=billCycle_obj.bill_cycle_code,CURR_MONTH=str(int(uploadB30.month)-1)).count()
#         consumerDetails_count=ConsumerDetails.objects.filter(bill_cycle=billCycle_obj,month='201606').count()
#
#         percentage= float(consumerDetails_count)/float(rt_detiails_count)*100
#         print 'percentage===>',percentage
#         return round(percentage,2)
#     except Exception, e:
#         print 'Exception|customfilter|get_startDate', e
#         return '0'


# @register.filter
# def getTimeDuration(pn33download):
#     try:
#         print 'pn33download.bill_schedule.bill_cycle',pn33download.bill_schedule.bill_cycle
#         print 'pn33download.month',pn33download.month
#
#         currentTime=datetime.datetime.now()
#         starttime=pn33download.start_date
#
#         print 'currentTime',currentTime
#         print 'starttime',starttime
#         starttime = starttime.replace(tzinfo=None)
#         duration=currentTime-starttime
#         print 'duration',duration
#         result=divmod(duration.days * 86400 + duration.seconds, 60)
#         result=str(result[0])+' min '+str(result[1])+' sec'
#         return result
#     except Exception, e:
#         print 'Exception|customfilter|getTimeDuration', e
#         return None