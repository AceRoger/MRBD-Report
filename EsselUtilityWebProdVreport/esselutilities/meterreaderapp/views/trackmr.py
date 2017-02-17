import json
import pdb
from time import timezone
import datetime
import dateutil
from adminapp.models import City, UserProfile
from adminapp.models import BillCycle
from dispatch.models import MeterReading,JobCard,RouteDetail, RouteAssignment
from scheduleapp.models import BillScheduleDetails, BillSchedule
# from geopy.geocoders import GoogleV3
from adminapp.constraints import SHOW_MONTH
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
Months = {
    1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR',
    5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG',
    9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'}


def checkMonth(month):
    if month > 9:
        return str(month)
    else:
        return '0' + str(month)

@csrf_exempt
def track_mr(request,mr_id):
    data={}
    try:
        monthYears = []
        for month in range(0, SHOW_MONTH):
            date = datetime.date.today() - dateutil.relativedelta.relativedelta(months=month)
            monthYears.append({'value': str(date.year) + checkMonth(date.month),
                               'text': Months[date.month] + ' ' + str(date.year)})
        data={'monthYears': monthYears,'mr_id':mr_id}

        print 'data', data

    except Exception, e:
      print 'Exception', e
    return render(request,'meterreaderapp/detail_track_mr.html', data)

@csrf_exempt
def get_cycle(request):
    try:

        final_list=[]
        month=request.POST.get('monthYear')
        userObj = UserProfile.objects.get(id=request.POST.get('mr_id'))

        routeAssignmented = RouteAssignment.objects.filter(meterreader=userObj,reading_month=month)

        final_list = []
        temp_list=[]

        for cycle in routeAssignmented:
            bill_cycle_temp=cycle.routedetail.billcycle.bill_cycle_code
            if bill_cycle_temp not in temp_list:
                temp_list.append(bill_cycle_temp)
                final_list.append({'id':cycle.routedetail.billcycle.id,'billCycle':bill_cycle_temp})

        data = {'success': 'true', 'billCycle': final_list}

    except Exception, e:
        print 'Exception|track_mr.py|get_cycle', e
        data = {'success': 'false', 'error': 'Exception ' + str(e)}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_routes(request):
    try:

        final_list=[]

        month=request.POST.get('monthYear')
        userObj = UserProfile.objects.get(id=request.POST.get('mr_id'))
        billCycle=BillCycle.objects.get(id=request.POST.get('billCycle'))
        routeAssignmented = RouteAssignment.objects.filter(meterreader=userObj,reading_month=month,routedetail__billcycle=billCycle)

        final_list = []
        temp_list=[]

        for cycle in routeAssignmented:
            final_list.append({'id':cycle.routedetail.id,'route':cycle.routedetail.route_code})
        data = {'success': 'true', 'billCycle': final_list}
    except Exception, e:
        print 'Exception|track_mr.py|get_cycle', e
        data = {'success': 'false', 'error': 'Exception ' + str(e)}
    return HttpResponse(json.dumps(data), content_type='application/json')



@csrf_exempt
def get_route_path(request):
    try:

        final_list=[]

        month=request.POST.get('monthYear')
        userObj = UserProfile.objects.get(id=request.POST.get('mr_id'))
        billCycle=BillCycle.objects.get(id=request.POST.get('billCycle'))
        route=RouteDetail.objects.get(id=request.POST.get('route'))
        meterReading=MeterReading.objects.filter(jobcard__consumerdetail__route=route,reading_month=month).order_by('reading_date')

        meterReading=meterReading.filter().exclude(longitude='0').exclude(latitude='0')


        final_list = []
        for reading in meterReading:
            if reading.longitude and reading.latitude:
                final_list.append({'longitude':reading.longitude,'latitude':reading.latitude})

        if final_list:
            data = {'success': 'true', 'locations': final_list}
        else:
            data = {'success': 'noreading'}

    except Exception, e:
        print 'Exception|track_mr.py|get_cycle', e
        data = {'success': 'false', 'error': 'Exception ' + str(e)}
    return HttpResponse(json.dumps(data), content_type='application/json')



@csrf_exempt
@login_required(login_url='/')
def get_routes01(request):
    route_list = []
    try:

        billcycle = BillCycle.objects.get(id=request.POST.get('billCycle'))

        route_objs=RouteDetail.objects.filter(billcycle=billcycle).order_by('route_code').values('route_code').distinct()
        for route in route_objs:
            options_data = '<option value=' + route['route_code'] + '>' + route['route_code'] + '</option>'
            route_list.append(options_data)

        data = {'route_list': route_list}

    except Exception, e:
        print 'Exception|track_mr.py|get_route_detail', e
        data = {'success': 'false', 'error': 'Exception ' + str(e)}
    return HttpResponse(json.dumps(data), content_type='application/json')

