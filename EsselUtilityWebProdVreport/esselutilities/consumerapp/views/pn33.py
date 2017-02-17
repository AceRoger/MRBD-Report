import json
import pdb
from django.http import HttpResponse
from django.shortcuts import render
import datetime
from adminapp import constraints
from adminapp.constraints import SHOW_MONTH
from consumerapp.models import RouteDetail, ConsumerDetails
from scheduleapp.models import BillSchedule, PN33Download, BillScheduleDetails
from adminapp.models import City, BillCycle, RT_MASTER, RT_DETAILS

from django.utils import timezone
from consumerapp.views import task
from django.contrib.auth.decorators import login_required
import dateutil.relativedelta
from authenticateapp.decorator import role_required

__author__ = 'vkm chandel'

Months = {
    1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR',
    5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG',
    9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'}

FILTER_BY = [{'value': 'All', 'text': 'All'},
             {'value': '0', 'text': 'Today'},
             {'value': '1', 'text': 'Tomorrow'}]


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def open_pn33_index(request):
    data = load_data()
    return render(request, 'consumerapp/pn33.html', data)


def load_data():
    try:
        monthYears = []
        for month in range(0, SHOW_MONTH):
            date = datetime.date.today() - dateutil.relativedelta.relativedelta(months=month)
            monthYears.append({'value': str(date.year) + checkMonth(date.month),
                               'text': Months[date.month] + ' ' + str(date.year)})

        pn33Downloads = PN33Download.objects.filter(month=monthYears[0]['value'], is_deleted=False).order_by('bill_schedule__bill_cycle__bill_cycle_code')
        total = pn33Downloads.filter().count()
        notStarted = pn33Downloads.filter(download_status='Not Started').count()
        started = pn33Downloads.filter(download_status='Started').count()
        failed = pn33Downloads.filter(download_status='Failed').count()
        Completed = pn33Downloads.filter(download_status='Completed').count()
        print 'billSchedule', pn33Downloads

        data = {'monthYears': monthYears, 'pn33Downloads': pn33Downloads,
                'NotStarted': notStarted, 'Started': started, 'Failed': failed,
                'Completed': Completed, 'Total': total, 'Filters': FILTER_BY
                }
        print data
    except Exception, e:
        print 'Exception|pn33.py|load_data', e
        data = {'message': 'Server Error'}
    return data


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def import_pn33(request):
    try:
        id = request.GET.get('id')
        pn33Download = PN33Download.objects.get(id=id)

        if pn33Download.download_status !='Started':

            yearMonth = constraints.month_minus(pn33Download.bill_schedule.month)
            bill_cycle_code=pn33Download.bill_schedule.bill_cycle.bill_cycle_code
            RT_MASTER.objects.filter(BILL_MONTH=yearMonth, BILL_CYC_CD=bill_cycle_code).delete()
            RT_DETAILS.objects.filter(BILL_CYC_CD=bill_cycle_code, CURR_MONTH=yearMonth).delete()
            RouteDetail.objects.filter(billcycle=pn33Download.bill_schedule.bill_cycle, month=yearMonth).delete()
            ConsumerDetails.objects.filter(bill_cycle=pn33Download.bill_schedule.bill_cycle, month=yearMonth).delete()

            taskObject = task.import_rtmaster.delay(pn33Download)

            print '---------Import Operation Started--------------',taskObject
            #taskObject = task.import_rtmaster.delay(pn33Download)
            pn33Download.start_date = timezone.now()
            pn33Download.download_status = 'Started'
            pn33Download.updated_by =request.user.email
            pn33Download.asy_job_id = taskObject.task_id
            pn33Download.save()

        data = {'success': 'true'}
    except Exception, e:
        print 'Exception|pn33|import_pn33', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_bill_cycles(request):
    try:
        #pdb.set_trace()
        print '=========================================================='
        print 'get_bill_cycles: request In, with', request.GET

        yearMonth = request.GET.get('yearMonth')
        pn33Downloads = PN33Download.objects.filter(month=yearMonth, is_deleted=False).order_by('bill_schedule__bill_cycle__bill_cycle_code')

        print 'pn33Downloads', pn33Downloads



        total = pn33Downloads.filter().count()
        notStarted = pn33Downloads.filter(download_status='Not Started').count()
        started = pn33Downloads.filter(download_status='Started').count()
        failed = pn33Downloads.filter(download_status='Failed').count()
        Completed = pn33Downloads.filter(download_status='Completed').count()

        data = {'pn33Downloads': pn33Downloads,
                'NotStarted': notStarted, 'Started': started, 'Failed': failed,
                'Completed': Completed, 'Total': total
                }

        print 'get_bill_cycles: response out, with', data
        data = render(request, 'consumerapp/billCyclesTailes.html', data)
    except Exception, e:
        print 'Exception|pn33.py|get_bill_cycles', e
        data = {'success': 'false', 'message': 'Server Error'}
    return HttpResponse(data)


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_bill_cycles_byfilter(request):
    try:

        print 'get_bill_cycles_byfilter: request In, with', request.GET

        yearMonth = request.GET.get('yearMonth')
        day = request.GET.get('filterBy')
        if day != 'All':
            filter_date = datetime.date.today() + datetime.timedelta(days=int(day))
            billScheduleDetails = BillScheduleDetails.objects.filter(start_date=filter_date, last_confirmed=True)
            print billScheduleDetails
            pn33Downloads = PN33Download.objects.filter(month=yearMonth,is_deleted=False, bill_schedule__in=[bs.billSchedule for bs in
                                                                                            billScheduleDetails]).order_by('bill_schedule__bill_cycle__bill_cycle_code')
        else:
            print 'yearMonth',yearMonth
            pn33Downloads = PN33Download.objects.filter(month=yearMonth,is_deleted=False).order_by('bill_schedule__bill_cycle__bill_cycle_code')

            print 'pn33Downloads',pn33Downloads

        total = pn33Downloads.filter().count()
        data = {'pn33Downloads': pn33Downloads,'Total': total}

        print 'get_bill_cycles_byfilter: response out, with', data
        data = render(request, 'consumerapp/billCyclesTailes.html', data)
    except Exception, e:
        print 'Exception|pn33.py|get_bill_cycles', e
        data = {'success': 'false', 'message': 'Server Error'}
    return HttpResponse(data)


def checkMonth(month):
    if month > 9:
        return str(month)
    else:
        return '0' + str(month)
