from django import template
from scheduleapp.models import BillSchedule
from datetime import date, timedelta

register = template.Library()

Months = {
    '01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR',
    '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AUG',
    '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'}

@register.filter
def checkBillSchedule(billcycle):
    try:
        billSchedule = BillSchedule.objects.get(bill_cycle=billcycle,is_uploaded=False)
        print "=====billScheduleDetails=======",billSchedule
        return 'Exist'
    except billSchedule.DoesNotExist:
        return 'NotExist'
    except Exception, e:
        print 'Exception|billCycleFilter|billCycleCode', e
        return None


@register.filter
def month(yearMonth):
    try:
        return Months[yearMonth[-2:]]
    except Exception, e:
        print 'Exception|billCycleFilter|month', e
        return None




@register.filter
def check_list(list, elements):
    elements = elements.split(',')
    flag = 'no'
    for element in elements:
        if element in list:
            flag = 'yes'
    if flag == 'yes':
        return 'true'
    else:
        return 'false'

