import datetime
from adminapp.models import RouteDetail, RT_DETAILS
from consumerapp.models import ConsumerDetails
from dispatch.models import JobCard, MeterReading, MeterStatus
from adminapp import constraints



__author__ = 'Vijay'

from django import template
from scheduleapp.models import BillSchedule, PN33Download, BillScheduleDetails

register = template.Library()

MONTHS = {
    '01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR',
    '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AUG',
    '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'}


@register.filter
def getBillDays(curr, prev):
    try:
        if type(curr) is not datetime.date:
            print "here"
            curr = curr.strftime("%d/%m/%Y %H:%M:%S")
            curr = datetime.datetime.strptime(curr,'%d/%m/%Y %H:%M:%S')
            curr = curr.date()

            prev

        if type(prev) is not datetime.date:
            print "here1"
            prev = prev.strftime("%d/%m/%Y %H:%M:%S")
            prev = datetime.datetime.strptime(prev,'%d/%m/%Y %H:%M:%S')
            prev = prev.date()

        # curr = datetime.strptime(curr, '%Y-%m-%d').date()
        # prev = datetime.strptime(prev, '%Y-%m-%d').date()

        # if type(curr) is not datetime.date:
        #     pass
        # else:
        #     curr = curr.date()

        # if type(prev) is not datetime.date:
        #     pass
        # else:
        #     prev = prev.date()

        if curr and prev:
            print "Billing days"
            print curr
            print prev

            delta = curr - prev
            return delta.days
        else:
            return None
    except Exception, e:
        print 'Exception|validatefilter|getBillDays', e
        return None

@register.filter
def getConsumption(prev_reading, curr_reading):
    try:
        # if int(curr_reading) > 0 and int(float(prev_reading)) > 0:
        consumption = int(float(curr_reading)) - int(float(prev_reading))
        return consumption
        # else:
        #     return None
    except Exception, e:
        print 'Exception|getConsumption|getBillDays', e
        return None


@register.filter
def getPrevReading(prev_reading):
    try:
        return int(float(prev_reading))
    except Exception, e:
        print 'Exception|getPrevReading|getBillDays', e
        return None

@register.filter
def getFisrtImage(consumer):
    try:
        jobcard = JobCard.objects.filter(consumerdetail__consumer_no = consumer.consumer_no, is_active = True, is_deleted = False, reading_month = consumer.month).first()
        meterReading = MeterReading.objects.filter(jobcard = jobcard).first()
        return meterReading.image_url
    except:
        return None

@register.filter
def getSecondImage(consumer):
    monthToShow = constraints.month_minus(consumer.month)
    try:
        jobcard = JobCard.objects.filter(consumerdetail__consumer_no = consumer.consumer_no, is_active = True, is_deleted = False, reading_month = monthToShow).first()
        meterReading = MeterReading.objects.filter(jobcard = jobcard).first()
        return meterReading.image_url
    except:
        return None

@register.filter
def getThirdImage(consumer):
    monthToShow = constraints.month_minus(consumer.month)
    monthToShow = constraints.month_minus(monthToShow)
    try:
        jobcard = JobCard.objects.filter(consumerdetail__consumer_no = consumer.consumer_no, is_active = True, is_deleted = False, reading_month = monthToShow).first()
        meterReading = MeterReading.objects.filter(jobcard = jobcard).first()
        return meterReading.image_url
    except:
        return None

@register.filter
def getFourthImage(consumer):
    monthToShow = constraints.month_minus(consumer.month)
    monthToShow = constraints.month_minus(monthToShow)
    monthToShow = constraints.month_minus(monthToShow)
    try:
        jobcard = JobCard.objects.filter(consumerdetail__consumer_no = consumer.consumer_no, is_active = True, is_deleted = False, reading_month = monthToShow).first()
        meterReading = MeterReading.objects.filter(jobcard = jobcard).first()
        return meterReading.image_url
    except:
        return None

@register.filter
def getFifthImage(consumer):
    monthToShow = constraints.month_minus(consumer.month)
    monthToShow = constraints.month_minus(monthToShow)
    monthToShow = constraints.month_minus(monthToShow)
    monthToShow = constraints.month_minus(monthToShow)
    try:
        jobcard = JobCard.objects.filter(consumerdetail__consumer_no = consumer.consumer_no, is_active = True, is_deleted = False, reading_month = monthToShow).first()
        meterReading = MeterReading.objects.filter(jobcard = jobcard).first()
        return meterReading.image_url
    except:
        return None

@register.filter
def getSixthImage(consumer):
    monthToShow = constraints.month_minus(consumer.month)
    monthToShow = constraints.month_minus(monthToShow)
    monthToShow = constraints.month_minus(monthToShow)
    monthToShow = constraints.month_minus(monthToShow)
    monthToShow = constraints.month_minus(monthToShow)
    try:
        jobcard = JobCard.objects.filter(consumerdetail__consumer_no = consumer.consumer_no, is_active = True, is_deleted = False, reading_month = monthToShow).first()
        meterReading = MeterReading.objects.filter(jobcard = jobcard).first()
        return meterReading.image_url
    except:
        return None


@register.filter
def getMeterStatus(meter_code):
    try:
        meterStatus=MeterStatus.objects.get(status_code=meter_code)
        return meterStatus.meter_status
    except:
        return None


meterStatus = {
    'DFCT':'Meter Faulty',
    'INAC':'Inaccesssible',
    'LOCK':'Locked Premise',
    'MISS':'Meter Missing',
    'NORM':'Normal',
    'NRDG':'Reading Not Taken',
    'OVR' :'Meter Overflow',
    'RPLC':'Meter Change',
}


@register.filter
def getNewMeterStatus(meter_code):
    try:
        print '-----get meter status-----'
        meterStatusChr=meterStatus[meter_code]
        return meterStatusChr
    except Exception,e:
	print 'Exception|getNetMeterStatus|',e
        return meter_code


