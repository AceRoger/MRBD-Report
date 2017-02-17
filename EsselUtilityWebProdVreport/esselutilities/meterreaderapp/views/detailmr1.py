import json
# import pdb
import pdb
import csv
import datetime
from adminapp.models import City
from adminapp.models import EmployeeType
from adminapp.models import UserProfile
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from meterreaderapp.models import DeviceDetail, PreferredRoutes
from adminapp.models import RouteDetail, BillCycle
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dispatch.models import RouteAssignment, JobCard, MeterReading
from adminapp.models import Availability
from adminapp.constraints import SHOW_MONTH
from consumerapp.models import ConsumerDetails
from scheduleapp.models import BillScheduleDetails
import datetime
import dateutil.relativedelta
# from consumerapp.models import ConsumerDetails
from django.contrib.auth.decorators import login_required
from authenticateapp.decorator import role_required

Months = {
    1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR',
    5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG',
    9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'}

# details Of Meter Reader  render to the card and edit form also
@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def detail_mr(request, mr_id, month = None):
    data = {}
    finallist = []

    currentmonth = None
    if month:
        currentmonth = month
    else:
        currentmonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month)
    try:
        monthYears = []
        for month in range(0, SHOW_MONTH):
            date = datetime.date.today() - dateutil.relativedelta.relativedelta(months=month)
            # date = datetime.date.today() - datetime.timedelta(month * 365 / 12)
            monthYears.append({'value': str(date.year) + checkMonth(date.month),
                               'text': Months[date.month] + ' ' + str(date.year)})
        yearMonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month)

        citys = City.objects.filter(is_deleted=False)

        deviceDetail_obj = DeviceDetail.objects.get(user_id_id=mr_id)
        companyName = deviceDetail_obj.company_name
        deviceID = deviceDetail_obj.device_name
        Make = deviceDetail_obj.make
        IMEI = deviceDetail_obj.imei_no
        deviceData = {'companyName': companyName, 'deviceID': deviceID, 'Make': Make, 'IMEI': IMEI}

        userPofile_obj = UserProfile.objects.get(id=mr_id)
        # for userPofile_obj in userPofile_list:

        name = userPofile_obj.first_name + ' ' + userPofile_obj.last_name
        firstname = userPofile_obj.first_name
        lastname = userPofile_obj.last_name
        address = userPofile_obj.address_line_1
        employee_id = userPofile_obj.employee_id
        email = userPofile_obj.email
        city = userPofile_obj.city
        status = userPofile_obj.status
        phone = userPofile_obj.contact_no
        # This id we used in edit model later on save edit details
        mrid = userPofile_obj.user_ptr_id

        billCycle = BillCycle.objects.filter(is_deleted=False)
        preferredRoutes = PreferredRoutes.objects.filter(user=userPofile_obj)

        availability = Availability.objects.get(validator=userPofile_obj)

        try:
            is_reading_completed = False
            jobcard = 0

            # get route count
            routeassignments = RouteAssignment.objects.filter(meterreader=mr_id, is_active=True,
                                                              is_deleted=False,reading_month=currentmonth,)  # reading_month=currentmonth

            for routeassignment in routeassignments:

                if routeassignment.is_reading_completed:
                    routestatus="Completed"
                else:
                    routestatus="Active"

                # get count for total readings
                jobcard = len(JobCard.objects.filter(meterreader=mr_id, routeassigned=routeassignment, is_active=True,
                                                     is_deleted=False,
                                                     is_reading_completed=True,reading_month=currentmonth,))  # reading_month=currentmonth

                # get count of total consumer
                totalconsumer =len(ConsumerDetails.objects.filter(route=routeassignment.routedetail, bill_month=currentmonth, is_deleted=False))
                objlist = {
                    #get billcycle code
                    'billcycle':routeassignment.routedetail.billcycle.bill_cycle_code,
                    'route': routeassignment.routedetail.route_code,
                    'totalconsumer': totalconsumer,
                    'jobcard': jobcard,
                    'routestatus':routestatus
                }
                finallist.append(objlist)

        except Exception, e:
            print 'Exception', e

        mrData = {'finallist': finallist, 'mrid': mrid, 'city': city, 'firstname': firstname, 'lastname': lastname,
                  'address': address,'employee_id': employee_id, 'phone': phone, 'name': name, 'status': status, 'email': email,
                  'availability': availability, 'preferredRoutes': preferredRoutes}

        data = {'monthYears': monthYears, 'currentmonth': currentmonth, 'mrData': mrData, 'deviceData': deviceData,
                'finallist': finallist, 'citys': citys, 'billCycle': billCycle,}
                    # 'currentmonth' : currentmonth, 'count': len(routeassignments)
    except Exception, e:
        print 'Exception', e
    return render(request, 'meterreaderapp/detail_mr.html', data)


def checkMonth(month):
    if month > 9:
        return str(month)
    else:
        return '0' + str(month)


# set statrt date and end date of perticular user
@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def update_availability(request):
    try:
        if request.POST:
            userProfile = UserProfile.objects.get(user_ptr_id=request.POST.get('mr_id'))
            available = Availability.objects.get(validator=userProfile)

            if request.POST.get('chkmode') == "Available":
                available.available = "AVAILABLE"

            elif request.POST.get('chkmode') == "Notavailable":
                available.available = 'NOT_AVAILABLE'

                available.start_date = datetime.datetime.strptime(request.POST.get('startDate'), '%d/%m/%Y')
                available.end_date = datetime.datetime.strptime(request.POST.get('endDate'), '%d/%m/%Y')
            available.save()

        data = {'success': 'true'}
    except Exception, e:
        print 'Exception|delailmr|update_availability|', e
        data = {'success': 'false', 'error': 'Exception '}
    return HttpResponse(json.dumps(data), content_type='application/json')


# Edit models data save into the database of meterreader
@csrf_exempt
@transaction.atomic
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def edit_save_mr(request):

    try:
        sid = transaction.savepoint()  # Transaction open
        if request.POST:

            if check_employee_id(request.POST.get('employeeId'), request.POST.get('email')):
                data = {'success': 'exist'}
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                city = City.objects.get(id=request.POST.get('mrCity'))
                userProfile = UserProfile.objects.get(id=request.POST.get('mrid'))
                userProfile.first_name = request.POST.get('firstName')
                userProfile.last_name = request.POST.get('lastName')
                userProfile.address_line_1 = request.POST.get('address')
                userProfile.contact_no = request.POST.get('contactNo')
                userProfile.city = city
                userProfile.employee_id = request.POST.get('employeeId')
            if request.POST.get('check_pwdchange_status') == 'change_password':
                userProfile.set_password(request.POST.get('password'))

            userProfile.save()


            deviceDetail = DeviceDetail.objects.get(user_id_id=request.POST.get('mrid'))
            deviceDetail.company_name = request.POST.get('companyName')
            deviceDetail.device_name = request.POST.get('deviceId')
            deviceDetail.make = request.POST.get('mrMake')
            deviceDetail.imei_no = request.POST.get('mrIMEI')
            deviceDetail.save()

            PreferredRoutes.objects.filter(user=userProfile).delete()
            PreferredRoutes(bill_cycle_code=BillCycle.objects.get(id=request.POST.get('billCycleOne')),
                            route=request.POST.get('routeDetailOne'), user=userProfile, preference_no='1').save()
            PreferredRoutes(bill_cycle_code=BillCycle.objects.get(id=request.POST.get('billCycleTwo')),
                            route=request.POST.get('routeDetailTwo'), user=userProfile, preference_no='2').save()
            PreferredRoutes(bill_cycle_code=BillCycle.objects.get(id=request.POST.get('billCycleThree')),
                            route=request.POST.get('routeDetailThree'), user=userProfile, preference_no='3').save()
            PreferredRoutes(bill_cycle_code=BillCycle.objects.get(id=request.POST.get('billCycleFour')),
                            route=request.POST.get('routeDetailFour'), user=userProfile, preference_no='4').save()

            transaction.savepoint_commit(sid)
            data = {'success': 'true'}
        else:
            data = {'success': 'false', 'error': 'Method type is not a POST!'}

    except Exception, e:
        print 'Exception|delailmr|edit_save_mr|', e
        data = {'success': 'false', 'error': 'Exception '}
    return HttpResponse(json.dumps(data), content_type='application/json')


    # check condition for Employee Id is Unique


@csrf_exempt
def check_employee_id(employeeid, email_id):
    try:
        # userProfile=UserProfile.objects.get(email=email_id)
        UserProfile.objects.get(Q(employee_id=employeeid), ~Q(email=email_id))
        return True
    except UserProfile.DoesNotExist:
        return False
    except Exception, e:
        print 'Exception|detailmr.py|check_existing_employee_id', e


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_meterreader(request):
    try:
        finallist = []
        yearMonth = request.GET.get('yearMonth')
        mr_id = request.GET.get('mr_id')
        print "yearMonth", yearMonth
        is_reading_completed = False
        # yearMonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month)
        routeassignments = RouteAssignment.objects.filter(meterreader=mr_id, is_active=True, is_deleted=False,
                                                          reading_month=yearMonth)  # reading_month=currentmonth

        for routeassignment in routeassignments:



            jobcard = len(JobCard.objects.filter(meterreader=mr_id, routeassigned=routeassignment, is_active=True,
                                                 reading_month=yearMonth,
                                                 is_deleted=False,
                                                 is_reading_completed=True))  # reading_month=currentmonth
            totalconsumer = len(
                JobCard.objects.filter(meterreader=mr_id, routeassigned=routeassignment, is_active=True,
                                       reading_month=yearMonth))
            if jobcard == 0:
                totalreading = 0
            else:
                totalreading = (float(jobcard) / float(totalconsumer)) * 100
                totalreading = int(totalreading)
                if totalreading == 100:
                    is_reading_completed = True
            objlist = {
                'billcycle': routeassignment.routedetail.billcycle.bill_cycle_code,
                'month': routeassignment.reading_month,
                'route': routeassignment.routedetail.route_code,
                'totalconsumer': totalconsumer,
                'totalreading': totalreading,
                'is_reading_completed': is_reading_completed,
                'jobcard': jobcard,
            }
            finallist.append(objlist)
        mrData = {'finallist': finallist, 'yearMonth': yearMonth, 'count': len(routeassignments)}

        data = render(request, 'meterreaderapp/detail_mr_2.html', mrData)
    except Exception, e:
        print 'Exception', e
    return data



@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def reading_export_materreader(request, mr_id, currentmonth):
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="readings_mr_' + str(
            currentmonth) + '.csv"';
        writer = csv.writer(response)
        writer.writerow(['Bill Cycle', 'Route', 'Consumers', 'Readings','Status'])  #'Month',

        routeassignments = RouteAssignment.objects.filter(meterreader=mr_id, is_active=True,
                                                          is_deleted=False,reading_month=currentmonth)  # reading_month=currentmonth
        for routeassignment in routeassignments:
            if routeassignment.is_reading_completed:
                routestatus = "Completed"
            else:
                routestatus = "Active"
            jobcard = len(JobCard.objects.filter(meterreader=mr_id, routeassigned=routeassignment, is_active=True,
                                                 is_deleted=False,
                                                 is_reading_completed=True,reading_month=currentmonth))



            totalconsumer = len(ConsumerDetails.objects.filter(route=routeassignment.routedetail, bill_month=currentmonth,
                                               is_deleted=False))

            billcycle = routeassignment.routedetail.billcycle.bill_cycle_code
            route = routeassignment.routedetail.route_code
            tempList = []

            # tempList.append(currentmonth)
            tempList.append(billcycle)
            tempList.append(route)
            tempList.append(totalconsumer)
            tempList.append(jobcard)
            tempList.append(routestatus)

            writer.writerow(tempList)

        return response
    except Exception, e:
        print 'Exception|detailmr.py|reading_export', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')