import csv
import json
# import pdb
import pdb
from time import timezone
import datetime

from adminapp.models import City
from adminapp.models import UserProfile
from adminapp.models import Availability
from adminapp.constraints import SHOW_MONTH
from django.http import HttpResponse
from django.shortcuts import render
from adminapp.models import BillCycle
from meterreaderapp.models import PreferredBillCycle
from django.views.decorators.csrf import csrf_exempt
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from dispatch.models import RouteAssignment

# details Of Validators render to the card and edit form also
from dispatch.models import ValidatorAssignment, RouteDetail, MeterReading
from dispatch.models import RouteAssignment, JobCard, MeterReading
from scheduleapp.models import BillScheduleDetails
import datetime
import dateutil.relativedelta
from authenticateapp.decorator import role_required

Months = {
    1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR',
    5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG',
    9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'}


@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def detail_validator(request, validator_id, month = None):
    # pdb.set_trace()
    data = {}
    data_obj = {}
    finallist = []
    final_list2 = []

    currentmonth = None
    if month:
        currentmonth = month
    else:
        currentmonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month)
    try:
        monthYears = []
        for month in range(0, SHOW_MONTH):
            date = datetime.date.today() - dateutil.relativedelta.relativedelta(months=month)

            monthYears.append({'value': str(date.year) + checkMonth(date.month),
                               'text': Months[date.month] + ' ' + str(date.year)})
        yearMonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month)
        citys = City.objects.filter(is_deleted=False)

        for city in citys:
            billCycle = BillCycle.objects.filter(is_deleted=False)
            userPofile_obj = UserProfile.objects.get(id=validator_id)
            preferredBillCycle = PreferredBillCycle.objects.filter(user=userPofile_obj)
            # for userPofile_obj in userPofile_list:
            name = userPofile_obj.first_name + ' ' + userPofile_obj.last_name
            firstname = userPofile_obj.first_name
            lastname = userPofile_obj.last_name
            address = userPofile_obj.address_line_1
            employee_id = userPofile_obj.employee_id
            email = userPofile_obj.email
            type = userPofile_obj.type
            city = userPofile_obj.city
            phone = userPofile_obj.contact_no
            status = userPofile_obj.status

        if preferredBillCycle:
            billCycle1 = preferredBillCycle.filter(preference_no='1')[0].bill_cycle_code
            billCycle2 = preferredBillCycle.filter(preference_no='2')[0].bill_cycle_code
        else:
            billCycle1 = ''
            billCycle2 = ''

        validatorid = userPofile_obj.user_ptr_id
        availability = Availability.objects.get(validator=userPofile_obj)

        billschedules = BillScheduleDetails.objects.filter(last_confirmed=True, month=currentmonth)
        for billschedule in billschedules:
            # jobcardbillcycle=JobCard.objects.filter(is_active=True)
            billcycle= billschedule.billSchedule.bill_cycle
            try:
                validatorreadingrecived = ValidatorAssignment.objects.filter(user_id=validator_id,
                                                                             meterreading__jobcard__routeassigned__routedetail__billcycle_id=billcycle,
                                                                         reading_month=currentmonth,meterreading__jobcard__is_active=True)
            except Exception,e:
                print e
                pass
            if validatorreadingrecived:
                readingrecived = len(validatorreadingrecived)
                validatorvalidated = ValidatorAssignment.objects.filter(user=validator_id,meterreading__jobcard__routeassigned__routedetail__billcycle_id=billcycle,
                                                                        reading_month=currentmonth, is_validated=True,meterreading__jobcard__is_active=True)
                validatedrecord = len(validatorvalidated)
                pending=readingrecived - validatedrecord
                objects = {
                    'month':currentmonth,
                    'readingrecived': readingrecived,
                    'validatedrecord': validatedrecord,
                    'billcycle': billcycle,
                    'pending':pending
                }
                finallist.append(objects)
            else:
                pass
        validatorData = {'validatorid': validator_id, 'availability': availability, 'type': type, 'city': city,
                         'firstname': firstname, 'lastname': lastname, 'address': address, 'employee_id': employee_id,
                         'phone': phone, 'name': name, 'email': email, 'status': status, 'billCycle1': billCycle1,
                         'billCycle2': billCycle2, 'finallist': finallist}


        data = {'monthYears': monthYears, 'currentmonth': currentmonth, 'validatorData': validatorData, 'citys': citys,
                'billCycle': billCycle, 'finallist': finallist}

    except Exception, e:
        print 'Exception', e
    return render(request, 'meterreaderapp/detailvalidator.html', data)


def checkMonth(month):
    if month > 9:
        return str(month)
    else:
        return '0' + str(month)


# Edit validator models data save into the database
@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def edit_save_validator(request):
    # pdb.set_trace()
    try:

        if request.POST:
            city = City.objects.get(id=request.POST.get('valCity'))


            print 'check_employee_id(request.POST.get('')', check_employee_id(request.POST.get('employeeId'),
                                                                              request.POST.get('email'))
            if check_employee_id(request.POST.get('employeeId'), request.POST.get('email')):
                data = {'success': 'exist'}
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                userProfile = UserProfile.objects.get(id=request.POST.get('validatorid'))
                userProfile.first_name = request.POST.get('firstName')
                userProfile.last_name = request.POST.get('lastName')
                userProfile.address_line_1 = request.POST.get('address')
                userProfile.contact_no = request.POST.get('contactNo')
                userProfile.city = city
                userProfile.employee_id = request.POST.get('employeeId')

            if request.POST.get('check_pwdchange_status') == 'change_password':
                userProfile.set_password(request.POST.get('password'))

            userProfile.save()

            PreferredBillCycle.objects.filter(user=userProfile).delete()
            PreferredBillCycle(bill_cycle_code=request.POST.get('prefBillCycleOne'), user=userProfile,
                               preference_no='1').save()
            PreferredBillCycle(bill_cycle_code=request.POST.get('prefBillCycleTwo'), user=userProfile,
                               preference_no='2').save()

            data = {'success': 'true'}
        else:
            data = {'success': 'false', 'error': 'Method type is  a POST!'}

    except Exception, e:
        print 'Exception|edit_save_validator', e
        data = {'success': 'false', 'error': 'Exception '}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def check_employee_id(employeeid, email_id):
    try:
        # userProfile=UserProfile.objects.get(email=email_id)
        UserProfile.objects.get(Q(employee_id=employeeid), ~Q(email=email_id))
        return True
    except UserProfile.DoesNotExist:
        return False
    except Exception, e:
        print 'Exception|detailvalidator.py|check_existing_employee_id', e


@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def update_validator_availability(request):
    try:
        if request.POST:
            userProfile = UserProfile.objects.get(user_ptr_id=request.POST.get('validatorid2'))
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
        print 'Exception|delailvalidator|update_validator_availability|', e
        data = {'success': 'false', 'error': 'Exception '}

    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_validator(request):
    try:
        data = {}
        finallist = []
        yearMonth = request.GET.get('yearMonth')
        validator = request.GET.get('validator')
        billschedules = BillScheduleDetails.objects.filter(last_confirmed=True, month=yearMonth)
        for billschedule in billschedules:
            billcycle = billschedule.billSchedule.bill_cycle
            try:
                validatorreadingrecived = ValidatorAssignment.objects.filter(user_id=validator_id,
                                                                             meterreading__jobcard__routeassigned__routedetail__billcycle_id=billcycle,
                                                                             reading_month=yearMonth)
            except Exception, e:
                print e
                pass
            if validatorreadingrecived:
                readingrecived = len(validatorreadingrecived)
                validatorvalidated = ValidatorAssignment.objects.filter(user=validator_id,
                                                                        meterreading__jobcard__routeassigned__routedetail__billcycle_id=billcycle,
                                                                        reading_month=yearMonth, is_validated=True)
                validatedrecord = len(validatorvalidated)
                pending = readingrecived - validatedrecord

                objects = {
                    'month':ValidatorAssignment.reading_month,
                    'readingrecived': readingrecived,
                    'validatedrecord': validatedrecord,
                    'billcycle': billcycle,
                    'pending': pending
                }
                finallist.append(objects)

        validatorData = {'yearMonth': yearMonth, 'finallist': finallist}
        data = render(request, 'meterreaderapp/detail_validator_2.html', validatorData)
    except Exception, e:
        print 'Exception', e
    return data


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def reading_export_validator(request, validator_id,currentmonth):
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="readings_mr_' + str(
            currentmonth) + '.csv"';
        writer = csv.writer(response)
        writer.writerow(['Month', 'Bill Cycle', 'Readings', 'Completed', 'Pendings'])

        billschedules = BillScheduleDetails.objects.filter(last_confirmed=True, month=currentmonth)
        for billschedule in billschedules:
            billcycle = billschedule.billSchedule.bill_cycle
            try:
                validatorreadingrecived = ValidatorAssignment.objects.filter(user_id=validator_id,
                                                                             meterreading__jobcard__routeassigned__routedetail__billcycle_id=billcycle,
                                                                             reading_month=currentmonth,meterreading__jobcard__is_active=True)

            except Exception, e:
                print e
                pass
            if validatorreadingrecived:
                readingrecived = len(validatorreadingrecived)
                validatorvalidated = ValidatorAssignment.objects.filter(user=validator_id,
                                                                        meterreading__jobcard__routeassigned__routedetail__billcycle_id=billcycle,
                                                                        reading_month=currentmonth, is_validated=True,meterreading__jobcard__is_active=True)

                validatedrecord = len(validatorvalidated)
                pending = readingrecived - validatedrecord
                tempList = []

                tempList.append(currentmonth)
                tempList.append(billcycle)
                tempList.append(readingrecived)
                tempList.append(validatedrecord)
                tempList.append(pending)

                writer.writerow(tempList)

        return response
    except Exception, e:
        print 'Exception|detailvalidator.py|reading_export_validator', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')