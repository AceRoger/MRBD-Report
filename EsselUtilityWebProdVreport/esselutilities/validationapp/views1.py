import csv
import json
import pdb
import smtplib
import base64
import MySQLdb, sys
from time import timezone
from django.utils import timezone
import datetime
import traceback
from django.shortcuts import render, render_to_response, redirect
from django.core.urlresolvers import reverse
# Create your views here
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control

from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.db import transaction
from django.shortcuts import render
from dispatch.models import MeterStatus,RouteAssignment,JobCard,ReaderStatus,MeterReading, ValidatorAssignment, UnbilledConsumerAssignment, UnbilledConsumerAssignmentCount, ValidatorAssignmentCount
from scheduleapp.models import BillSchedule,PN33Download,BillScheduleDetails
from adminapp.models import State,City,Utility,EmployeeType,UserProfile,UserPrivilege,UserRole,BillCycle,RouteDetail, UPLD_MTR_RDNG, Availability
from consumerapp.models import ConsumerDetails, UnBilledConsumers
from meterreaderapp.models import DeviceDetail,PreferredRoutes
from django.db.models import Q
from adminapp.constraints import SHOW_MONTH
from django.db import transaction
# importing exceptions
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.contrib.messages import get_messages
import dateutil.relativedelta
from authenticateapp.decorator import role_required

Month = {
    '01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR',
    '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AUG',
    '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'}

Months = {
    1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR',
    5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG',
    9: 'SEPT', 10: 'OCT', 11: 'NOV', 12: 'DEC'}

def checkMonth(month):
    if month > 9:
        return str(month)
    else:
        return '0' + str(month)

def monthhh(yearMonth):
    try:
        return Month[yearMonth[-2:]]
    except Exception, e:
        print 'Exception|billCycleFilter|month', e
        return None

# Create your views here.
@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def validate_jobcard_list(request, month = None):
    data = {}
    finallist = []
    objlist = {}
    overAllConsumers = 0
    overAllReadingsReceived = 0
    overAllValidated = 0
    overAllValidatedV1 = 0
    overAllValidatedV2 = 0
    monthYears = []
    currentmonth = None
    if month:
        currentmonth = month
    else:
        currentmonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month )
    try:
        monthYears = []
        for month in range(0, SHOW_MONTH):
            date = datetime.date.today() - dateutil.relativedelta.relativedelta(months=month)
            #date = datetime.date.today() - datetime.timedelta(month * 365 / 12)
            monthYears.append({'value': str(date.year) + checkMonth(date.month),
                               'text': Months[date.month] + ' ' + str(date.year)})

        yearMonth=str(datetime.date.today().year) + checkMonth(datetime.date.today().month)
    except:
        pass
    monthh=monthhh(currentmonth)
    try:
        billcycles = BillCycle.objects.all()
        for billcycle in billcycles:
            validatorAssigned = False
            billschedule = None
            readingreceived = 0
            meterReadingCompleted = 0
            meterReadingCompletedV1 = 0
            meterReadingCompletedV2 = 0
            meterReadingDuplicate = 0
            validationStarted = False
            validationPercentage = 0
            try:
                billschedule = BillSchedule.objects.get(bill_cycle=billcycle, month = currentmonth)
            except:
                pass
            if billschedule:
                try:
                    billScheduledetail = BillScheduleDetails.objects.get(billSchedule=billschedule, month = currentmonth, last_confirmed = True)

                    routes = RouteDetail.objects.filter(billcycle=billcycle, bill_month = currentmonth)

                    for route in routes:
                        routeassigned = RouteAssignment.objects.filter(routedetail=route, reading_month = currentmonth)

                        for routeassignedOne in routeassigned:
                            jobCards = JobCard.objects.filter(routeassigned=routeassignedOne, is_reading_completed = True,record_status = 'COMPLETED', reading_month = currentmonth, is_deleted = False, is_active = True)
                            readingreceived = readingreceived + len(jobCards)
                            # query for completed meter readings
                            meterReading = MeterReading.objects.filter(jobcard__routeassigned=routeassignedOne,  reading_status = 'complete', reading_month = currentmonth, is_deleted = False, is_duplicate = False, is_active = True).count()
                            meterReadingCompleted = meterReadingCompleted + int(meterReading)

                            meterReadingV1 = MeterReading.objects.filter(jobcard__routeassigned=routeassignedOne,  reading_status = 'validation1', reading_month = currentmonth, is_deleted = False, is_duplicate = False, is_active = True).count()
                            meterReadingCompletedV1 = meterReadingCompletedV1 + int(meterReadingV1)

                            meterReadingV2 = MeterReading.objects.filter(jobcard__routeassigned=routeassignedOne,  reading_status = 'validation2', reading_month = currentmonth, is_deleted = False, is_duplicate = False, is_active = True).count()
                            meterReadingCompletedV2 = meterReadingCompletedV2 + int(meterReadingV2)

                            meterReadingD = MeterReading.objects.filter(jobcard__routeassigned=routeassignedOne,reading_month = currentmonth, is_duplicate = True, is_deleted = False, is_active = False)
                            meterReadingDuplicate = meterReadingDuplicate + int(len(meterReadingD))

                    overAllValidated = overAllValidated + meterReadingCompleted
                    overAllValidatedV1 = overAllValidatedV1 + meterReadingCompletedV1
                    overAllValidatedV2 = overAllValidatedV2 + meterReadingCompletedV2
                    overAllReadingsReceived = overAllReadingsReceived + int(readingreceived)

                    totalconsumer = ConsumerDetails.objects.filter(bill_cycle=billcycle, bill_month = currentmonth)
                    overAllConsumers = overAllConsumers + int(len(totalconsumer))

                    # check In this billcycle is there any meterreading assignment for loggedin validator
                    validatorAssignment = ValidatorAssignment.objects.filter(user = request.user.userprofile, meterreading__jobcard__routeassigned__routedetail__billcycle = billcycle)

                    if validatorAssignment and  len(validatorAssignment) > 0:
                        validatorAssigned = True
                    # fetch unbilled consumers
                    #UnbilledConsumerAssignment
                    unBilledConsumers = UnBilledConsumers.objects.filter(reading_month = currentmonth, is_confirmed = False, is_descarded = False ,bill_cycle_code = billcycle.bill_cycle_code)
                    unBilledConsumersCount = 0
                    if unBilledConsumers:
                        unBilledConsumersCount = len(unBilledConsumers)

                    objlist = {
                        'billcycle': billschedule,
                        'startdate': billScheduledetail.start_date.strftime('%d/%m/%Y'),
                        'billingdate': billScheduledetail.accounting_date.strftime('%d/%m/%Y'),
                        'readingreceived':readingreceived,
                        'totalconsumer': len(totalconsumer),
                        'meterReadingCompleted':meterReadingCompleted,
                        'meterReadingDuplicate':meterReadingDuplicate,
                        'unBilledConsumers': unBilledConsumersCount,
                        'validatorAssigned':validatorAssigned,
                        'validationStarted':validationStarted,
                        'validationPercentage':validationPercentage,
                        }
                    finallist.append(objlist)
                except Exception, e:
                    pass
        overAllPending = overAllReadingsReceived - overAllValidated
        data = {'finallists': finallist,'overAllConsumers':overAllConsumers, 'overAllReadingsReceived':overAllReadingsReceived,'overAllValidated':overAllValidated,'overAllValidatedV1':overAllValidatedV1,'overAllValidatedV2':overAllValidatedV2, 'overAllPending':overAllPending, 'monthYears':monthYears,  'currentmonth' : currentmonth, 'loggedinuser': request.user.userprofile, 'monthinwords':monthh }
    except Exception as e:
        print e
    return render(request, 'validationapp/validation1.html',data)

@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def validation_level_one(request, billcycle_id = None, month = None, validatorassigned_id = None):
    currentmonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month )
    totalReadingsAssigned = 0
    totalValidated = 0
    totalPending = 0
    formData = None
    billcycle = None
    route_id = None
    prevValidateRecord = None
    nextValidateRecord = None
    validatorassigned_id = validatorassigned_id
    #pulling out the meter status and reader status
    meter_status_values = MeterStatus.objects.all()
    reader_status_values = ReaderStatus.objects.all()
    billcycle = BillCycle.objects.get(id = billcycle_id)
    if validatorassigned_id:
        # validatorAssigned = ValidatorAssignment.objects.filter( ( Q(meterreading__reading_status = 'validation1') | Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )),user = request.user, sent_to_revisit = False, reading_month = currentmonth)
        validatorAssigned = ValidatorAssignment.objects.filter( ( Q(meterreading__reading_status = 'validation1') | Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )),user = request.user, sent_to_revisit = False, reading_month = month, meterreading__jobcard__routeassigned__routedetail__billcycle_id = billcycle_id, meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False)
        if validatorAssigned:
            totalReadingsAssigned = len(validatorAssigned)
            i = 0
            found = False
            for validatorAssignedOne in validatorAssigned:
                if validatorAssignedOne.id == int(validatorassigned_id):
                    if i == 0:
                        prevValidateRecord = None
                        if len(validatorAssigned) > (i+1):
                            nextValidateRecord = validatorAssigned[i+1].id
                    elif i == len(validatorAssigned) - 1:
                        prevValidateRecord = validatorAssigned[i-1].id
                        nextValidateRecord = None
                    else:
                        prevValidateRecord = validatorAssigned[i-1].id
                        nextValidateRecord = validatorAssigned[i+1].id
                else:
                    pass
                # for calculating totalvalidated
                if validatorAssignedOne.is_validated == True:
                    totalValidated = totalValidated + 1
                i = i +1
            totalPending = totalReadingsAssigned - totalValidated

            # show the main selected validate record
            validatorAssignedToShow = None
            try:
                # validatorAssignedToShow = ValidatorAssignment.objects.get(( Q(meterreading__reading_status = 'validation1') | Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )),id = validatorassigned_id,user = request.user, sent_to_revisit = False, reading_month = currentmonth)
                validatorAssignedToShow = ValidatorAssignment.objects.get(( Q(meterreading__reading_status = 'validation1') | Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )),id = validatorassigned_id,user = request.user, sent_to_revisit = False, reading_month = month, meterreading__jobcard__routeassigned__routedetail__billcycle_id = billcycle_id , meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False)

                formData = {
                    'consumer':validatorAssignedToShow.meterreading.jobcard.consumerdetail,
                    'meterreading':validatorAssignedToShow.meterreading,
                    'meterreader':validatorAssignedToShow.meterreading.jobcard.meterreader,
                    'validatorassigned_id': validatorAssignedToShow.id,
                    'is_validated' : validatorAssignedToShow.is_validated
                }
                route_id = validatorAssignedToShow.meterreading.jobcard.routeassigned.routedetail.route_code

            except ValidatorAssignment.DoesNotExist:
                pass
            return render(request,'validationapp/validationlevel1.html',{'totalReadingsAssigned':totalReadingsAssigned,'totalPending':totalPending,'totalValidated':totalValidated,'billcycle':billcycle,'route_id':route_id, 'data':formData, 'assigned':True,'prevValidateRecord':prevValidateRecord,'nextValidateRecord':nextValidateRecord,'reader_status_values':reader_status_values, 'meter_status_values':meter_status_values,'month':month})
        else:
            return render(request,'validationapp/validationlevel1.html',{'assigned':False ,'month':month, 'billcycle':billcycle})
    else:
        # code for validatorassigned_id is not provided
        # validatorAssigned = ValidatorAssignment.objects.filter( ( Q(meterreading__reading_status = 'validation1') | Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )),user = request.user, sent_to_revisit = False, reading_month = currentmonth)
        validatorAssigned = ValidatorAssignment.objects.filter( ( Q(meterreading__reading_status = 'validation1') | Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )),user = request.user, sent_to_revisit = False, reading_month = month, meterreading__jobcard__routeassigned__routedetail__billcycle_id = billcycle_id, meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False)
        if validatorAssigned:
            totalReadingsAssigned = len(validatorAssigned)
            i = 0
            found = False
            for validatorAssignedOne in validatorAssigned:
                if validatorAssignedOne.is_validated == True:
                    totalValidated = totalValidated + 1
                if found == False and validatorAssignedOne.is_validated == False:
                    # billcycle = BillCycle.objects.get(id = validatorAssignedOne.meterreading.jobcard.routeassigned.routedetail.billcycle.id)
                    formData = {
                        'consumer':validatorAssignedOne.meterreading.jobcard.consumerdetail,
                        'meterreading':validatorAssignedOne.meterreading,
                        'meterreader':validatorAssignedOne.meterreading.jobcard.meterreader,
                        'validatorassigned_id': validatorAssignedOne.id,
                        'is_validated' : validatorAssignedOne.is_validated
                    }
                    found = True
                    route_id = validatorAssignedOne.meterreading.jobcard.routeassigned.routedetail.route_code

                    if i == 0:
                        prevValidateRecord = None
                        if len(validatorAssigned) > (i+1):
                            nextValidateRecord = validatorAssigned[i+1].id
                    elif i == len(validatorAssigned) - 1:
                        prevValidateRecord = validatorAssigned[i-1].id
                        nextValidateRecord = None
                    else:
                        prevValidateRecord = validatorAssigned[i-1].id
                        nextValidateRecord = validatorAssigned[i+1].id
                i = i+1
            if found == False:
                # billcycle = BillCycle.objects.get(id = validatorAssigned.meterreading.jobcard.routeassigned.routedetail.billcycle.id)
                formData = {
                    'consumer':validatorAssigned[0].meterreading.jobcard.consumerdetail,
                    'meterreading':validatorAssigned[0].meterreading,
                    'meterreader':validatorAssigned[0].meterreading.jobcard.meterreader,
                    'validatorassigned_id': validatorAssigned[0].id,
                    'is_validated' : validatorAssigned[0].is_validated
                }
                route_id = validatorAssignedOne.meterreading.jobcard.routeassigned.routedetail.route_code
                prevValidateRecord = None
                if len(validatorAssigned) > 1:
                    nextValidateRecord = validatorAssigned[1].id

            totalPending = totalReadingsAssigned - totalValidated
            return render(request,'validationapp/validationlevel1.html',{'totalReadingsAssigned':totalReadingsAssigned,'totalPending':totalPending,'totalValidated':totalValidated,'billcycle':billcycle,'route_id':route_id, 'data':formData, 'assigned':True,'prevValidateRecord':prevValidateRecord,'nextValidateRecord':nextValidateRecord, 'reader_status_values':reader_status_values, 'meter_status_values':meter_status_values,'month':month})
        else:
            return render(request,'validationapp/validationlevel1.html',{'assigned':False,'month':month, 'billcycle':billcycle})


#TODO How to maintain validatorAssignmentCount across month
@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def validation_level_one_validate(request):
    billcycleidtopass = request.POST.get('billcycleidtopass')
    monthpass = request.POST.get('monthpass')
    #currentmonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month )
    if request.POST.get('validatorassignedid'):
        try:
            validatorAssigned = ValidatorAssignment.objects.get(user = request.user, sent_to_revisit = False, is_validated=False, id = request.POST.get('validatorassignedid'))

            meterReading = MeterReading.objects.get(id = validatorAssigned.meterreading_id)

            meterReadingDuplicate = MeterReading.objects.filter(jobcard__consumerdetail = meterReading.jobcard.consumerdetail, reading_month = meterReading.reading_month, is_active = False, is_deleted = False, is_duplicate = True)
            if meterReadingDuplicate:
                meterReading.is_active = False
                meterReading.is_deleted = False
                meterReading.is_duplicate = True
                meterReading.save()
                meterReading.jobcard.is_active = False
                meterReading.jobcard.record_status = 'DUPLICATE'
                meterReading.jobcard.save()
                messages.add_message(request, messages.INFO, 'Cant validate reading, found duplicate, Added reading in the duplicate bucket!')
                return HttpResponseRedirect(reverse('validate:validation_level_one', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))

            meterReadingDuplicate1 = 0
            meterReadingDuplicate1 = MeterReading.objects.filter(jobcard__consumerdetail = meterReading.jobcard.consumerdetail, reading_month = meterReading.reading_month, is_active = True, is_deleted = False, is_duplicate = False)

            if meterReadingDuplicate1 and len(meterReadingDuplicate1) > 1:
                meterReading.is_active = False
                meterReading.is_deleted = False
                meterReading.is_duplicate = True
                meterReading.save()
                meterReading.jobcard.is_active = False
                meterReading.jobcard.record_status = 'DUPLICATE'
                meterReading.jobcard.save()
                messages.add_message(request, messages.INFO, 'Cant validate reading, found duplicate, Added reading in the duplicate bucket!')
                return HttpResponseRedirect(reverse('validate:validation_level_one', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))

            meterReadingDuplicate2 = UPLD_MTR_RDNG.objects.filter(BILL_MONTH = meterReading.reading_month,CUSTOMER_ID = meterReading.jobcard.consumerdetail.consumer_no)

            if meterReadingDuplicate2:
                meterReading.is_active = False
                meterReading.is_deleted = False
                meterReading.is_duplicate = True
                meterReading.save()
                meterReading.jobcard.is_active = False
                meterReading.jobcard.record_status = 'DUPLICATE'
                meterReading.jobcard.save()
                messages.add_message(request, messages.INFO, 'Cant validate reading, found duplicate, Added reading in the duplicate bucket!')
                return HttpResponseRedirect(reverse('validate:validation_level_one', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))
            else:
                validatorAssigned.remark = request.POST.get('comment_v1')
                validatorAssigned.is_validated = True
                validatorAssigned.save()

                meterReading.reading_status = 'validation2'

                meterReading.meter_status_v1 = (MeterStatus.objects.get(meter_status = request.POST.get('meter_status_v1') ))
                meterReading.reader_status_v1 = (ReaderStatus.objects.get(reader_status = request.POST.get('reader_status_v1')))
                meterReading.comment_v1 = request.POST.get('comment_v1')
                meterReading.current_meter_reading_v1 = request.POST.get('current_meter_reading_v1')
                meterReading.image_remark_v1 = request.POST.get('image_remark_v1')

                meterReading.Updated_on = timezone.now()
                meterReading.updated_by = request.user.username

                meterReading.updated_by_v1 = request.user.userprofile
                meterReading.validated_on_v1 = timezone.now()
                meterReading.save()

                try:
                    validatorAssignmentCount = ValidatorAssignmentCount.objects.get(user_id = request.user.userprofile.id)

                    if validatorAssignmentCount.count > 0:
                        validatorAssignmentCount.count = validatorAssignmentCount.count - 1
                        validatorAssignmentCount.save()
                except Exception, e:
                    print e
                    pass

                if request.is_ajax():
                    data = {'success':'true'}
                    return HttpResponse(json.dumps(data), content_type='application/json')
                else:
                    messages.add_message(request, messages.INFO, 'Consumer validated successfully!')
                    return HttpResponseRedirect(reverse('validate:validation_level_one', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))
        except (ValidatorAssignment.DoesNotExist, MeterReading.DoesNotExist), e:
            print e
            print "An unexpected error is occured!"
            if request.is_ajax():
                data = {'success':'false'}
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                messages.add_message(request, messages.ERROR, 'An unexpected error is occured! Try again')
                return HttpResponseRedirect(reverse('validate:validation_level_one', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))


@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def validation_level_one_validate_complete(request):
    billcycleidtopass = request.POST.get('billcycleidtopass')
    monthpass = request.POST.get('monthpass')
    #currentmonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month )
    if request.POST.get('validatorassignedid'):
        try:
            validatorAssigned = ValidatorAssignment.objects.get(user = request.user, sent_to_revisit = False, is_validated=False, id = request.POST.get('validatorassignedid'))

            meterReading = MeterReading.objects.get(id = validatorAssigned.meterreading_id)

            meterReadingDuplicate = MeterReading.objects.filter(jobcard__consumerdetail = meterReading.jobcard.consumerdetail, reading_month = meterReading.reading_month, is_active = False, is_deleted = False, is_duplicate = True)

            if meterReadingDuplicate:
                meterReading.is_active = False
                meterReading.is_deleted = False
                meterReading.is_duplicate = True
                meterReading.save()
                meterReading.jobcard.is_active = False
                meterReading.jobcard.record_status = 'DUPLICATE'
                meterReading.jobcard.save()
                messages.add_message(request, messages.INFO, 'Cant validate reading, found duplicate, Added reading in the duplicate bucket!')
                return HttpResponseRedirect(reverse('validate:validation_level_one', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))

            meterReadingDuplicate1 = 0
            meterReadingDuplicate1 = MeterReading.objects.filter(jobcard__consumerdetail = meterReading.jobcard.consumerdetail, reading_month = meterReading.reading_month, is_active = True, is_deleted = False, is_duplicate = False)

            if meterReadingDuplicate1 and len(meterReadingDuplicate1) > 1:
                meterReading.is_active = False
                meterReading.is_deleted = False
                meterReading.is_duplicate = True
                meterReading.save()
                meterReading.jobcard.is_active = False
                meterReading.jobcard.record_status = 'DUPLICATE'
                meterReading.jobcard.save()
                messages.add_message(request, messages.INFO, 'Cant validate reading, found duplicate, Added reading in the duplicate bucket!')
                return HttpResponseRedirect(reverse('validate:validation_level_one', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))

            meterReadingDuplicate2 = UPLD_MTR_RDNG.objects.filter(BILL_MONTH = meterReading.reading_month,CUSTOMER_ID = meterReading.jobcard.consumerdetail.consumer_no)


            if meterReadingDuplicate2:
                meterReading.is_active = False
                meterReading.is_deleted = False
                meterReading.is_duplicate = True
                meterReading.save()
                meterReading.jobcard.is_active = False
                meterReading.jobcard.record_status = 'DUPLICATE'
                meterReading.jobcard.save()
                messages.add_message(request, messages.INFO, 'Cant validate reading, found duplicate, Added reading in the duplicate bucket!')
                return HttpResponseRedirect(reverse('validate:validation_level_one', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))
            else:

                validatorAssigned.remark = request.POST.get('comment_v1')
                validatorAssigned.is_validated = True
                validatorAssigned.save()


                meterReading.reading_status = 'complete'

                meterReading.meter_status_v1 = (MeterStatus.objects.get(meter_status = request.POST.get('meter_status_v1') ))
                meterReading.reader_status_v1 = (ReaderStatus.objects.get(reader_status = request.POST.get('reader_status_v1')))
                meterReading.comment_v1 = request.POST.get('comment_v1')
                meterReading.current_meter_reading_v1 = request.POST.get('current_meter_reading_v1')

                meterReading.meter_status_v2 = (MeterStatus.objects.get(meter_status = request.POST.get('meter_status_v1') ))
                meterReading.reader_status_v2 = (ReaderStatus.objects.get(reader_status = request.POST.get('reader_status_v1')))
                meterReading.comment_v2 = request.POST.get('comment_v1')
                meterReading.current_meter_reading_v2 = request.POST.get('current_meter_reading_v1')

                meterReading.Updated_on = timezone.now()
                meterReading.updated_by = request.user.username

                meterReading.updated_by_v1 = request.user.userprofile
                meterReading.validated_on_v1 = timezone.now()
                meterReading.updated_by_v2 = request.user.userprofile
                meterReading.validated_on_v2 = timezone.now()

                meterReading.save()

                try:
                    validatorAssignmentCount = ValidatorAssignmentCount.objects.get(user_id = request.user.userprofile.id)
                    if validatorAssignmentCount.count > 0:
                        validatorAssignmentCount.count = validatorAssignmentCount.count - 1
                        validatorAssignmentCount.save()
                except:
                    pass

                if request.is_ajax():
                    data = {'success':'true'}
                    return HttpResponse(json.dumps(data), content_type='application/json')
                else:
                    messages.add_message(request, messages.INFO, 'Consumer validated successfully!')
                    return HttpResponseRedirect(reverse('validate:validation_level_one', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))
        except (ValidatorAssignment.DoesNotExist, MeterReading.DoesNotExist), e:
            print e
            print "An unexpected error is occured!"
            if request.is_ajax():
                data = {'success':'false'}
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                messages.add_message(request, messages.ERROR, 'An unexpected error is occured! Try again')
                return HttpResponseRedirect(reverse('validate:validation_level_one', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))

@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def validation_level_two(request, billcycle_id = None, month = None, validatorassigned_id = None):
    currentmonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month )
    totalReadingsAssigned = 0
    totalValidated = 0
    totalPending = 0
    formData = None
    billcycle = None
    route_id = None
    validatorAssignedDummy = None
    prevValidateRecord = None
    nextValidateRecord = None
    validatorassigned_id = validatorassigned_id
    # fetching meter and reader status values
    meter_status_values = MeterStatus.objects.all()
    reader_status_values = ReaderStatus.objects.all()
    billcycle = BillCycle.objects.get(id = billcycle_id)
    if validatorassigned_id:
        # validatorAssigned = ValidatorAssignment.objects.filter( (Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )), user = request.user, sent_to_revisit = False, reading_month = currentmonth)
        validatorAssigned = ValidatorAssignment.objects.filter( (Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )), user = request.user, sent_to_revisit = False , reading_month = month, meterreading__jobcard__routeassigned__routedetail__billcycle_id = billcycle_id , meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False)
        if validatorAssigned:
            totalReadingsAssigned = len(validatorAssigned)
            i = 0
            found = False
            for validatorAssignedOne in validatorAssigned:
                if validatorAssignedOne.id == int(validatorassigned_id):
                    if i == 0:
                        prevValidateRecord = None
                        if len(validatorAssigned) > (i+1):
                            nextValidateRecord = validatorAssigned[i+1].id
                    elif i == len(validatorAssigned) - 1:
                        prevValidateRecord = validatorAssigned[i-1].id
                        nextValidateRecord = None
                    else:
                        prevValidateRecord = validatorAssigned[i-1].id
                        nextValidateRecord = validatorAssigned[i+1].id
                else:
                    pass

                # for calculating totalvalidated
                if validatorAssignedOne.is_validated == True:
                    totalValidated = totalValidated + 1
                i = i +1
            totalPending = totalReadingsAssigned - totalValidated

            # show the main selected validate record
            validatorAssignedToShow = None
            try:

                # validatorAssignedToShow = ValidatorAssignment.objects.get((Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )),id = validatorassigned_id,user = request.user, sent_to_revisit = False, reading_month = currentmonth)
                validatorAssignedToShow = ValidatorAssignment.objects.get((Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )),id = validatorassigned_id,user = request.user, sent_to_revisit = False, reading_month = month, meterreading__jobcard__routeassigned__routedetail__billcycle_id = billcycle_id , meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False)
                formData = {
                    'consumer':validatorAssignedToShow.meterreading.jobcard.consumerdetail,
                    'meterreading':validatorAssignedToShow.meterreading,
                    'meterreader':validatorAssignedToShow.meterreading.jobcard.meterreader,
                    'validatorassigned_id': validatorAssignedToShow.id,
                    'is_validated' : validatorAssignedToShow.is_validated
                }
                route_id = validatorAssignedToShow.meterreading.jobcard.routeassigned.routedetail.route_code

                # for taking the remark from validator one
                try:
                    validatorAssignedDummy = ValidatorAssignment.objects.get(assigned_to = 'validator1',meterreading = validatorAssignedToShow.meterreading, is_validated = True, sent_to_revisit = False, meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False)
                except ValidatorAssignment.DoesNotExist:
                    pass

            except ValidatorAssignment.DoesNotExist:
                pass
            return render(request,'validationapp/validationlevel2.html',{'totalReadingsAssigned':totalReadingsAssigned,'totalPending':totalPending,'totalValidated':totalValidated,'billcycle':billcycle,'route_id':route_id, 'data':formData, 'assigned':True,'prevValidateRecord':prevValidateRecord,'nextValidateRecord':nextValidateRecord, 'previousValidatorRemark':validatorAssignedDummy.remark if validatorAssignedDummy else '',  'reader_status_values':reader_status_values, 'meter_status_values':meter_status_values,'month':month})
        else:
            return render(request,'validationapp/validationlevel2.html',{'assigned':False,'month':month, 'billcycle':billcycle})
    else:
        # code for validatorassigned_id is not provided
        # validatorAssigned = ValidatorAssignment.objects.filter( (Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )),user = request.user, sent_to_revisit = False, reading_month = currentmonth)
        validatorAssigned = ValidatorAssignment.objects.filter( (Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )),user = request.user, sent_to_revisit = False, reading_month = month, meterreading__jobcard__routeassigned__routedetail__billcycle_id = billcycle_id, meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False)
        if validatorAssigned:
            totalReadingsAssigned = len(validatorAssigned)
            i = 0
            found = False
            for validatorAssignedOne in validatorAssigned:
                if validatorAssignedOne.is_validated == True:
                    totalValidated = totalValidated + 1
                if found == False and validatorAssignedOne.is_validated == False:
                    formData = {
                        'consumer':validatorAssignedOne.meterreading.jobcard.consumerdetail,
                        'meterreading':validatorAssignedOne.meterreading,
                        'meterreader':validatorAssignedOne.meterreading.jobcard.meterreader,
                        'validatorassigned_id': validatorAssignedOne.id,
                        'is_validated' : validatorAssignedOne.is_validated
                    }
                    found = True
                    route_id = validatorAssignedOne.meterreading.jobcard.routeassigned.routedetail.route_code

                    # for taking the remark from validator one
                    try:
                        validatorAssignedDummy = ValidatorAssignment.objects.get(assigned_to = 'validator1',meterreading = validatorAssignedOne.meterreading, is_validated = True, meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False)
                    except ValidatorAssignment.DoesNotExist:
                        pass

                    if i == 0:
                        prevValidateRecord = None
                        if len(validatorAssigned) > (i+1):
                            nextValidateRecord = validatorAssigned[i+1].id
                    elif i == len(validatorAssigned) - 1:
                        prevValidateRecord = validatorAssigned[i-1].id
                        nextValidateRecord = None
                    else:
                        prevValidateRecord = validatorAssigned[i-1].id
                        nextValidateRecord = validatorAssigned[i+1].id
                i = i+1
            if found == False:
                formData = {
                    'consumer':validatorAssigned[0].meterreading.jobcard.consumerdetail,
                    'meterreading':validatorAssigned[0].meterreading,
                    'meterreader':validatorAssigned[0].meterreading.jobcard.meterreader,
                    'validatorassigned_id': validatorAssigned[0].id,
                    'is_validated' : validatorAssigned[0].is_validated
                }
                route_id = validatorAssigned[0].meterreading.jobcard.routeassigned.routedetail.route_code

                # for taking the remark from validator one
                try:
                    validatorAssignedDummy = ValidatorAssignment.objects.get(assigned_to = 'validator1',meterreading = validatorAssigned[0].meterreading, is_validated = True, sent_to_revisit = False, meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False)
                except ValidatorAssignment.DoesNotExist:
                    pass
                # assign prev and next

                prevValidateRecord = None
                if len(validatorAssigned) > 1:
                    nextValidateRecord = validatorAssigned[1].id

            totalPending = totalReadingsAssigned - totalValidated
            return render(request,'validationapp/validationlevel2.html',{'totalReadingsAssigned':totalReadingsAssigned,'totalPending':totalPending,'totalValidated':totalValidated,'billcycle':billcycle,'route_id':route_id, 'data':formData, 'assigned':True,'prevValidateRecord':prevValidateRecord,'nextValidateRecord':nextValidateRecord, 'previousValidatorRemark':validatorAssignedDummy.remark if validatorAssignedDummy else '','reader_status_values':reader_status_values, 'meter_status_values':meter_status_values,'month':month})
        else:
            return render(request,'validationapp/validationlevel2.html',{'assigned':False,'month':month, 'billcycle':billcycle})


#TODO How to maintain validatorAssignmentCount across month
@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def validation_level_two_validate(request):
    billcycleidtopass = request.POST.get('billcycleidtopass')
    monthpass = request.POST.get('monthpass')
    #currentmonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month )
    if request.POST.get('validatorassignedid'):
        try:
            validatorAssigned = ValidatorAssignment.objects.get(user = request.user, sent_to_revisit = False, is_validated=False, id = request.POST.get('validatorassignedid'))

            meterReading = MeterReading.objects.get(id = validatorAssigned.meterreading_id)
            # for checking if any duplicate reading is there present
            meterReadingDuplicate = MeterReading.objects.filter(jobcard__consumerdetail = meterReading.jobcard.consumerdetail, reading_month = meterReading.reading_month, is_active = False, is_deleted = False, is_duplicate = True)

            if meterReadingDuplicate:
                meterReading.is_active = False
                meterReading.is_deleted = False
                meterReading.is_duplicate = True
                meterReading.save()
                meterReading.jobcard.is_active = False
                meterReading.jobcard.record_status = 'DUPLICATE'
                meterReading.jobcard.save()
                messages.add_message(request, messages.INFO, 'Cant validate reading, found duplicate, Added reading in the duplicate bucket!')
                return HttpResponseRedirect(reverse('validate:validation_level_one', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))

            meterReadingDuplicate1 = 0
            meterReadingDuplicate1 = MeterReading.objects.filter(jobcard__consumerdetail = meterReading.jobcard.consumerdetail, reading_month = meterReading.reading_month, is_active = True, is_deleted = False, is_duplicate = False)

            if meterReadingDuplicate1 and len(meterReadingDuplicate1) > 1:
                meterReading.is_active = False
                meterReading.is_deleted = False
                meterReading.is_duplicate = True
                meterReading.save()
                meterReading.jobcard.is_active = False
                meterReading.jobcard.record_status = 'DUPLICATE'
                meterReading.jobcard.save()
                messages.add_message(request, messages.INFO, 'Cant validate reading, found duplicate, Added reading in the duplicate bucket!')
                return HttpResponseRedirect(reverse('validate:validation_level_one', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))



            meterReadingDuplicate2 = UPLD_MTR_RDNG.objects.filter(BILL_MONTH = meterReading.reading_month,CUSTOMER_ID = meterReading.jobcard.consumerdetail.consumer_no)

            if meterReadingDuplicate2:
                meterReading.is_active = False
                meterReading.is_deleted = False
                meterReading.is_duplicate = True
                meterReading.save()
                meterReading.jobcard.is_active = False
                meterReading.jobcard.record_status = 'DUPLICATE'
                meterReading.jobcard.save()
                messages.add_message(request, messages.INFO, 'Cant validate reading, found duplicate, Added reading in the duplicate bucket!')
                return HttpResponseRedirect(reverse('validate:validation_level_one', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))
            else:
                validatorAssigned.remark = request.POST.get('remark')
                validatorAssigned.is_validated = True
                validatorAssigned.save()

                meterReading.reading_status = 'complete'

                meterReading.meter_status_v2 = (MeterStatus.objects.get(meter_status = request.POST.get('meter_status_v2') ))
                meterReading.reader_status_v2 = (ReaderStatus.objects.get(reader_status = request.POST.get('reader_status_v2')))
                meterReading.comment_v2 = request.POST.get('comment_v2')
                meterReading.current_meter_reading_v2 = request.POST.get('current_meter_reading_v2')
                meterReading.image_remark_v2 = request.POST.get('image_remark_v2')

                meterReading.Updated_on = timezone.now()
                meterReading.updated_by = request.user.username

                meterReading.updated_by_v2 = request.user.userprofile
                meterReading.validated_on_v2 = timezone.now()

                meterReading.save()
                try:
                    validatorAssignmentCount = ValidatorAssignmentCount.objects.get(user_id = request.user.userprofile.id)
                    if validatorAssignmentCount.count > 0:
                        validatorAssignmentCount.count = validatorAssignmentCount.count - 1
                        validatorAssignmentCount.save()
                except:
                    pass

                if request.is_ajax():
                    data = {'success':'true'}
                    return HttpResponse(json.dumps(data), content_type='application/json')
                else:
                    messages.add_message(request, messages.INFO, 'Consumer validated successfully!')
                    return HttpResponseRedirect(reverse('validate:validation_level_two', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))
        except (ValidatorAssignment.DoesNotExist, MeterReading.DoesNotExist), e:
            print e
            print "An unexpected error is occured!"
            if request.is_ajax():
                data = {'success':'false'}
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                messages.add_message(request, messages.ERROR, 'An unexpected error is occured! Try again')
                return HttpResponseRedirect(reverse('validate:validation_level_two', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))


@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def validation_level_one_revisit(request):
    billcycleidtopass = request.POST.get('billcycleidtopass')
    monthpass = request.POST.get('monthpass')
    if request.POST.get('validatorassignedid'):
        try:
            validatorAssigned = ValidatorAssignment.objects.get(user = request.user, sent_to_revisit = False, is_validated=False, id = request.POST.get('validatorassignedid'))
            validatorAssigned.sent_to_revisit = True
            validatorAssigned.save()

            validatorAssigned.meterreading.reading_status = 'revisit'
            validatorAssigned.meterreading.is_deleted = True
            validatorAssigned.meterreading.is_active = False

            validatorAssigned.meterreading.jobcard.record_status = 'REVISIT'
            validatorAssigned.meterreading.jobcard.is_active = False
            validatorAssigned.meterreading.jobcard.save()

            validatorAssigned.meterreading.updated_by = request.user.username
            validatorAssigned.meterreading.Updated_on = datetime.date.today()
            validatorAssigned.meterreading.save()

            jobcard = JobCard(
                        routeassigned = validatorAssigned.meterreading.jobcard.routeassigned,
                        consumerdetail = validatorAssigned.meterreading.jobcard.consumerdetail,
                        completion_date = validatorAssigned.meterreading.jobcard.completion_date,
                        reading_month= validatorAssigned.meterreading.jobcard.reading_month,
                        created_by = request.user.username,
                        is_revisit =True,
                    )
            jobcard.save()

            try:
                validatorAssignmentCount = ValidatorAssignmentCount.objects.get(user_id = request.user.userprofile.id)
                if validatorAssignmentCount.count > 0:
                    validatorAssignmentCount.count = validatorAssignmentCount.count - 1
                    validatorAssignmentCount.save()
            except:
                pass

            messages.add_message(request, messages.ERROR, 'Consumer sent to revisit successfully!')
            return HttpResponseRedirect(reverse('validate:validation_level_one' , kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))
        except ValidatorAssignment.DoesNotExist, e:
            messages.add_message(request, messages.ERROR, 'An unexpected error is occured! Try again')
            return HttpResponseRedirect(reverse('validate:validation_level_one', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))
    else:
        messages.add_message(request, messages.ERROR, 'An unexpected error is occured! Try again')
        return HttpResponseRedirect(reverse('validate:validation_level_one', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))

@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def validation_level_two_revisit(request):
    billcycleidtopass = request.POST.get('billcycleidtopass')
    monthpass = request.POST.get('monthpass')
    if request.POST.get('validatorassignedid'):
        try:
            validatorAssigned = ValidatorAssignment.objects.get(user = request.user, sent_to_revisit = False, is_validated=False, id = request.POST.get('validatorassignedid'))
            validatorAssigned.sent_to_revisit = True
            validatorAssigned.save()

            validatorAssigned.meterreading.reading_status = 'revisit'
            validatorAssigned.meterreading.is_deleted = True
            validatorAssigned.meterreading.is_active = False

            validatorAssigned.meterreading.jobcard.record_status = 'REVISIT'
            validatorAssigned.meterreading.jobcard.is_active = False
            validatorAssigned.meterreading.jobcard.save()

            validatorAssigned.meterreading.updated_by = request.user.username
            validatorAssigned.meterreading.Updated_on = datetime.date.today()
            validatorAssigned.meterreading.save()

            jobcard = JobCard(
                        routeassigned = validatorAssigned.meterreading.jobcard.routeassigned,
                        consumerdetail = validatorAssigned.meterreading.jobcard.consumerdetail,
                        completion_date = validatorAssigned.meterreading.jobcard.completion_date,
                        reading_month= validatorAssigned.meterreading.jobcard.reading_month,
                        created_by = request.user.username,
                        is_revisit =True,
                    )
            jobcard.save()

            try:
                validatorAssignmentCount = ValidatorAssignmentCount.objects.get(user_id = request.user.userprofile.id)
                if validatorAssignmentCount.count > 0:
                    validatorAssignmentCount.count = validatorAssignmentCount.count - 1
                    validatorAssignmentCount.save()
            except:
                pass

            messages.add_message(request, messages.ERROR, 'Consumer sent to revisit successfully!')
            return HttpResponseRedirect(reverse('validate:validation_level_two', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))
        except ValidatorAssignment.DoesNotExist, e:
            messages.add_message(request, messages.ERROR, 'An unexpected error is occured! Try again')
            return HttpResponseRedirect(reverse('validate:validation_level_two', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))
    else:
        messages.add_message(request, messages.ERROR, 'An unexpected error is occured! Try again')
        return HttpResponseRedirect(reverse('validate:validation_level_two', kwargs={'billcycle_id': billcycleidtopass,'month':monthpass}))


# TODO listview will be of all months
@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def validation_level_one_listview(request ,billcycle_id = None, month = None):
    totalReadingsAssigned = 0
    totalValidated = 0
    totalPending = 0
    formData = None
    billcycle = None
    route_id = None
    allData = []
    validatorAssigned = ValidatorAssignment.objects.filter((Q(meterreading__reading_status = 'validation1') | Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )), user = request.user.userprofile, sent_to_revisit = False, reading_month = month, meterreading__jobcard__routeassigned__routedetail__billcycle_id = billcycle_id, meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False)
    if validatorAssigned:
        totalReadingsAssigned = len(validatorAssigned)
        for validatorAssignedOne in validatorAssigned:
            if validatorAssignedOne.is_validated == True:
                totalValidated = totalValidated + 1
            billcycle = BillCycle.objects.get(id = validatorAssignedOne.meterreading.jobcard.routeassigned.routedetail.billcycle.id)
            route_id = validatorAssignedOne.meterreading.jobcard.routeassigned.routedetail.id
            route_code = validatorAssignedOne.meterreading.jobcard.routeassigned.routedetail.route_code
            formData = {
                'consumer':validatorAssignedOne.meterreading.jobcard.consumerdetail,
                'meterreading':validatorAssignedOne.meterreading,
                'meterreader':validatorAssignedOne.meterreading.jobcard.meterreader,
                'validatorassigned_id': validatorAssignedOne.id,
                'is_validated' : validatorAssignedOne.is_validated,
                'route_id': route_id,
                'route_code':route_code,
            }
            allData.append(formData)
        totalPending = totalReadingsAssigned - totalValidated
        return render(request,'validationapp/validation_level_one_listview.html',{'totalReadingsAssigned':totalReadingsAssigned,'totalPending':totalPending,'totalValidated':totalValidated, 'alldata':allData, 'assigned':True, 'billcycle': billcycle, 'month': month})
    else:
        return render(request,'validationapp/validation_level_one_listview.html',{'assigned':False})



@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def validation_level_one_list_export(request ,billcycle_id = None, month = None):
    try:
        billcycle = BillCycle.objects.get(id = billcycle_id)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="validation1_readings_' + str(
            billcycle.bill_cycle_code) + '_' + str(month) +  '.csv"';
        writer = csv.writer(response)
        writer.writerow(['RouteID', 'Consumer Number', 'Meter Number', 'Consumer Name', 'Meter Reader Name', 'Current Reading','Status'])

        billcycle = None
        route_id = None
        allData = []
        validatorAssigned = ValidatorAssignment.objects.filter((Q(meterreading__reading_status = 'validation1') | Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )), user = request.user.userprofile, sent_to_revisit = False, reading_month = month, meterreading__jobcard__routeassigned__routedetail__billcycle_id = billcycle_id, meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False)
        if validatorAssigned:
            totalReadingsAssigned = len(validatorAssigned)
            for validatorAssignedOne in validatorAssigned:
                billcycle = BillCycle.objects.get(id = validatorAssignedOne.meterreading.jobcard.routeassigned.routedetail.billcycle.id)
                route_id = validatorAssignedOne.meterreading.jobcard.routeassigned.routedetail.id
                route_code = validatorAssignedOne.meterreading.jobcard.routeassigned.routedetail.route_code

                tempList = []
                tempList.append(str(route_code))
                tempList.append(str("'")+str(validatorAssignedOne.meterreading.jobcard.consumerdetail.consumer_no).encode('utf-8'))
                tempList.append(str(validatorAssignedOne.meterreading.jobcard.consumerdetail.meter_no))
                tempList.append(validatorAssignedOne.meterreading.jobcard.consumerdetail.name)
                tempList.append(( validatorAssignedOne.meterreading.jobcard.meterreader.first_name + ' ' + validatorAssignedOne.meterreading.jobcard.meterreader.last_name).encode('utf-8'))
                tempList.append(validatorAssignedOne.meterreading.current_meter_reading)
                if validatorAssignedOne.is_validated:
                    tempList.append('Sent to validator2')
                else:
                    tempList.append('Pending')

                writer.writerow(tempList)
        return response
    except Exception, e:
        print e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

# TODO list will be of all months
@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def validation_level_two_listview(request ,billcycle_id = None, month = None):
    totalReadingsAssigned = 0
    totalValidated = 0
    totalPending = 0
    formData = None
    billcycle = None
    route_id = None
    allData = []
    validatorAssigned = ValidatorAssignment.objects.filter((Q(meterreading__reading_status='validation2') | Q(meterreading__reading_status='complete')), user=request.user.userprofile, sent_to_revisit=False, reading_month = month, meterreading__jobcard__routeassigned__routedetail__billcycle_id = billcycle_id, meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False)
    if validatorAssigned:
        totalReadingsAssigned = len(validatorAssigned)
        for validatorAssignedOne in validatorAssigned:
            if validatorAssignedOne.is_validated == True:
                totalValidated = totalValidated + 1
            billcycle = BillCycle.objects.get(
                id=validatorAssignedOne.meterreading.jobcard.routeassigned.routedetail.billcycle.id)
            route_id = validatorAssignedOne.meterreading.jobcard.routeassigned.routedetail.id
            route_code = validatorAssignedOne.meterreading.jobcard.routeassigned.routedetail.route_code
            formData = {
                'consumer': validatorAssignedOne.meterreading.jobcard.consumerdetail,
                'meterreading': validatorAssignedOne.meterreading,
                'meterreader': validatorAssignedOne.meterreading.jobcard.meterreader,
                'validatorassigned_id': validatorAssignedOne.id,
                'is_validated': validatorAssignedOne.is_validated,
                'route_id': route_id,
                'route_code':route_code,
            }
            allData.append(formData)
        totalPending = totalReadingsAssigned - totalValidated
        return render(request, 'validationapp/validation_level_two_listview.html',
                      {'totalReadingsAssigned': totalReadingsAssigned, 'totalPending': totalPending,
                       'totalValidated': totalValidated, 'alldata': allData, 'assigned': True, 'billcycle': billcycle, 'month': month})
    else:
        return render(request, 'validationapp/validation_level_two_listview.html', {'assigned': False})

@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def validation_level_two_list_export(request ,billcycle_id = None, month = None):
    try:
        billcycle = BillCycle.objects.get(id = billcycle_id)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="validation2_readings_' + str(
            billcycle.bill_cycle_code) + '_' + str(month) +  '.csv"';
        writer = csv.writer(response)
        writer.writerow(['RouteID', 'Consumer Number', 'Meter Number', 'Consumer Name', 'Meter Reader Name', 'Current Reading','Status'])

        billcycle = None
        route_id = None
        allData = []
        validatorAssigned = ValidatorAssignment.objects.filter((Q(meterreading__reading_status='validation2') | Q(meterreading__reading_status='complete')), user=request.user.userprofile, sent_to_revisit=False, reading_month = month, meterreading__jobcard__routeassigned__routedetail__billcycle_id = billcycle_id, meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False)
        if validatorAssigned:
            totalReadingsAssigned = len(validatorAssigned)
            for validatorAssignedOne in validatorAssigned:
                billcycle = BillCycle.objects.get(id = validatorAssignedOne.meterreading.jobcard.routeassigned.routedetail.billcycle.id)
                route_id = validatorAssignedOne.meterreading.jobcard.routeassigned.routedetail.id
                route_code = validatorAssignedOne.meterreading.jobcard.routeassigned.routedetail.route_code

                tempList = []
                tempList.append(str(route_code))
                tempList.append(str("'")+str(validatorAssignedOne.meterreading.jobcard.consumerdetail.consumer_no).encode('utf-8'))
                tempList.append(str(validatorAssignedOne.meterreading.jobcard.consumerdetail.meter_no))
                tempList.append(validatorAssignedOne.meterreading.jobcard.consumerdetail.name)
                tempList.append(( validatorAssignedOne.meterreading.jobcard.meterreader.first_name + ' ' + validatorAssignedOne.meterreading.jobcard.meterreader.last_name).encode('utf-8'))
                tempList.append(validatorAssignedOne.meterreading.current_meter_reading)
                if validatorAssignedOne.is_validated:
                    tempList.append('Complete')
                else:
                    tempList.append('Pending')

                writer.writerow(tempList)
        return response
    except Exception, e:
        print e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def unbillconsumer(request, billcycle_id = None, month = None):
    unBilledConsumers = []
    totalunBilledConsumers = 0
    billCycle = BillCycle.objects.get(id = billcycle_id)
    try:
        unBilledConsumersTotal = UnBilledConsumers.objects.filter(reading_month = month, is_confirmed = False, bill_cycle_code = billCycle.bill_cycle_code)
        totalunBilledConsumers = len(unBilledConsumersTotal)
    except Exception, e:
        print e
    try:
        unbilledConsumerAssignment = UnbilledConsumerAssignment.objects.filter(user_id = request.user.userprofile.id,reading_month = month,is_confirmed = False, unbillconsumer__bill_cycle_code = billCycle.bill_cycle_code, unbillconsumer__is_descarded = False, unbillconsumer__is_confirmed = False)
        if unbilledConsumerAssignment:
            for unbilledConsumerAssignment1 in unbilledConsumerAssignment:
                unBilledConsumers.append(unbilledConsumerAssignment1)
    except:
        pass
    return render(request, 'validationapp/unbilllconsumer.html', {'data':unBilledConsumers, 'totalunBilledConsumers':totalunBilledConsumers,'billCycle':billCycle, 'month':month, 'monthtoshow':monthhh(month)})

@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def unbillconsumer_export(request, billcycle_id = None, month = None):
    try:
        billcycle = BillCycle.objects.get(id = billcycle_id)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="unbilled_consumers' + str(
            billcycle.bill_cycle_code) + '_' + str(month) +  '.csv"';
        writer = csv.writer(response)
        writer.writerow(['RouteID', 'Consumer Number', 'Meter Number', 'Consumer Name', 'Meter Reader Name', 'Current Reading'])

        unbilledConsumerAssignment = UnbilledConsumerAssignment.objects.filter(user_id = request.user.userprofile.id,reading_month = month,is_confirmed = False, unbillconsumer__bill_cycle_code = billcycle.bill_cycle_code, unbillconsumer__is_descarded = False, unbillconsumer__is_confirmed = False)
        if unbilledConsumerAssignment:
            for dataOne in unbilledConsumerAssignment:
                tempList = []
                tempList.append(str(dataOne.unbillconsumer.route_code))
                tempList.append(str("'")+str(dataOne.unbillconsumer.consumer_no).encode('utf-8'))
                tempList.append((dataOne.unbillconsumer.meter_no).encode('utf-8', 'ignore'))
                tempList.append((dataOne.unbillconsumer.name).encode('utf-8', 'ignore'))
                tempList.append(dataOne.unbillconsumer.meterreader.first_name + ' ' + dataOne.unbillconsumer.meterreader.last_name)
                tempList.append(dataOne.unbillconsumer.current_meter_reading)
                writer.writerow(tempList)
        return response
    except Exception, e:
        print 'exception ',str(traceback.print_exc())
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def unbillconsumerreview(request, billcycle_id = None, month = None, cons_id = None ):
    # fetching meter and reader status values
    meter_status_values = MeterStatus.objects.all()
    reader_status_values = ReaderStatus.objects.all()
    billCycle = BillCycle.objects.get(id = billcycle_id)
    try:
        unbilledConsumerAssignment = UnbilledConsumerAssignment.objects.filter(user = request.user)
        unbillconsumerToShow = None
        prevValidateRecord = None
        nextValidateRecord = None
        billcycles = []
        routestoshow = []
        found = False
        i = 0
        for unbilledConsumerAssignmentOne in unbilledConsumerAssignment:
            if found == False and unbilledConsumerAssignmentOne.unbillconsumer_id == int(cons_id):
                unbillconsumerToShow = unbilledConsumerAssignmentOne.unbillconsumer
                found = True
                if i == 0:
                    prevValidateRecord = None
                    if len(unbilledConsumerAssignment) > (i+1):
                        nextValidateRecord = unbilledConsumerAssignment[i+1].unbillconsumer.id
                elif i == len(unbilledConsumerAssignment) - 1:
                    prevValidateRecord = unbilledConsumerAssignment[i-1].unbillconsumer.id
                    nextValidateRecord = None
                else:
                    prevValidateRecord = unbilledConsumerAssignment[i-1].unbillconsumer.id
                    nextValidateRecord = unbilledConsumerAssignment[i+1].unbillconsumer.id
            i = i+1
        if found == False:
            unbillconsumerToShow = unbilledConsumerAssignment.unbillconsumer
            prevValidateRecord = None
            if len(unbilledConsumerAssignment) > 1:
                nextValidateRecord = unbilledConsumerAssignment[1].unbillconsumer.id

    except Exception, e:
        print e
        pass
    return render(request, 'validationapp/unbilllconsumerreview.html', {'consumer': unbillconsumerToShow,'prevValidateRecord':prevValidateRecord,'nextValidateRecord':nextValidateRecord,'billcycle_id':billcycle_id, 'month':month, 'monthtoshow':monthhh(month), 'reader_status_values':reader_status_values, 'meter_status_values':meter_status_values, 'billCycle':billCycle})


@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def verifyconsumer(request):
    unBilledConsumer = UnBilledConsumers.objects.get(id = request.POST.get('consumer_id'), is_confirmed = False)
    try:
        consumerDetails = ConsumerDetails.objects.get(consumer_no = unBilledConsumer.consumer_no, bill_cycle__id = request.POST.get('billcyclecode'), bill_month = request.POST.get('month'))
        data = {'success': 'true'}
    except ConsumerDetails.DoesNotExist:
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def discard_consumer(request):
    try:
        unBilledConsumer = UnBilledConsumers.objects.get(id = request.POST.get('consumer_id'), is_confirmed = False)
        unBilledConsumer.is_descarded = True

        unBilledConsumer.updated_by = request.user.username
        unBilledConsumer.Updated_on = datetime.date.today()
        unBilledConsumer.save()
        data = {'success': 'true'}

    except ConsumerDetails.DoesNotExist:
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def add_unbilled_consumer(request):
    meter_status_values = None
    reader_status_values = None
    routeDetail = None
    billcycle = None
    unBilledConsumer = None
    unbilledConsumerAssignment = None
    unbilledConsumerAssignmentCount = None
    try:
        unBilledConsumer = UnBilledConsumers.objects.get(id =request.POST.get('consumer_id'))
    except UnBilledConsumers.DoesNotExist:
        print "found excepion 1"
    try:
        unbilledConsumerAssignment = UnbilledConsumerAssignment.objects.get(user_id = request.user.userprofile.id, reading_month =request.POST.get('billmonth'), unbillconsumer = unBilledConsumer)
    except UnbilledConsumerAssignment.DoesNotExist:
        print "found exception 2"
    try:
        unbilledConsumerAssignmentCount = UnbilledConsumerAssignmentCount.objects.get(user_id = request.user.userprofile.id)
    except UnbilledConsumerAssignmentCount.DoesNotExist:
        print "found exception 3"

    try:
        meter_status_value = MeterStatus.objects.get(meter_status = unBilledConsumer.meter_status)
    except:
        meter_status_value = MeterStatus.objects.get(meter_status = 'Normal')
        pass

    try:
        reader_status_value = ReaderStatus.objects.get(reader_status = unBilledConsumer.reader_status)
    except:
        reader_status_value = ReaderStatus.objects.get(reader_status = 'Normal')
        pass

    routeDetail = RouteDetail.objects.filter(route_code = request.POST.get('route_id'), bill_month =request.POST.get('billmonth'))
    billCycle = BillCycle.objects.filter(bill_cycle_code = request.POST.get('billcycle_code'))
    if routeDetail and billCycle:
        pass
    else:
        unBilledConsumer.bill_cycle_code = request.POST.get('billcycle_code')
        unBilledConsumer.route_code = request.POST.get('route_id')
        unBilledConsumer.consumer_no = request.POST.get('consumer_no')
        unBilledConsumer.meter_no = request.POST.get('meter_no')
        unBilledConsumer.name = request.POST.get('consumer_name')
        unBilledConsumer.save()
         # Route is not yet assigned, Cant add consumer
        messages.add_message(request, messages.INFO, 'Cant add Reading! Route is not dispatched.')
        data = {'success': 'true', 'add':1} # 0 for cant add consumer
        return HttpResponse(json.dumps(data), content_type='application/json')
        # check consumer exist for given billcycle and billmonth and route

    try:
        consumerDetails = ConsumerDetails.objects.get(consumer_no = request.POST.get('consumer_no'), bill_month =request.POST.get('billmonth'))

        if str(consumerDetails.bill_cycle.bill_cycle_code) == str(request.POST.get('billcycle_code')):
            pass
        else:
            messages.add_message(request, messages.INFO, 'Cant add reading, Billcycle does not match.')
            data = {'success': 'true', 'add':8} # added as duplicate reading successfully
            return HttpResponse(json.dumps(data), content_type='application/json')

        # Check if route is assigned
        # Check if job card is created , then it will be a duplicate reading

        jobCard1 = JobCard.objects.filter(consumerdetail = consumerDetails, reading_month =request.POST.get('billmonth'))
        if(jobCard1):
            try:
                meterReading = MeterReading.objects.get(jobcard = jobCard1)
                jobCard = JobCard(
                    routeassigned = meterReading.jobcard.routeassigned,
                    consumerdetail = consumerDetails,
                    meterreader = unBilledConsumer.meterreader,
                    reading_month = request.POST.get('billmonth'),
                    is_reading_completed = True,
                    is_active = False,
                    record_status = 'DUPLICATE',
                    created_by = request.user.username,
                )
                jobCard.save()
                # save meter reading
                meterReading = MeterReading(
                    jobcard = jobCard,
                    current_meter_reading = unBilledConsumer.current_meter_reading,
                    image_url = unBilledConsumer.image_url,
                    longitude = unBilledConsumer.longitude,
                    latitude = unBilledConsumer.latitude,
                    reading_date = unBilledConsumer.reading_date,
                    reading_month = request.POST.get('billmonth'),
                    meter_status = meter_status_value,
                    reader_status = reader_status_value,
                    is_duplicate = True,
                    is_active = False,
                    suspicious_activity = unBilledConsumer.suspicious_activity,
                    suspicious_image_url = unBilledConsumer.suspicious_image_url,
                    suspicious_activity_remark = unBilledConsumer.suspicious_activity_remark,
                    comment = unBilledConsumer.comment,
                    comment_v1 = request.POST.get('remark_v1'),

                )
                meterReading.save()
                unBilledConsumer.is_confirmed = True
                unBilledConsumer.save()
                unbilledConsumerAssignment.is_confirmed = True
                unbilledConsumerAssignment.save()
                unbilledConsumerAssignmentCount.count = unbilledConsumerAssignmentCount.count - 1
                unbilledConsumerAssignmentCount.save()
                messages.add_message(request, messages.INFO, 'Cant add reading, reading already exist! Added to Duplicate reading bucket!')
                data = {'success': 'true', 'add':6} # added as duplicate reading successfully
                return HttpResponse(json.dumps(data), content_type='application/json')

            except MeterReading.DoesNotExist:
                try:
                    routeAssignment = RouteAssignment.objects.get(routedetail__route_code = request.POST.get('route_id'), reading_month = request.POST.get('billmonth'), routedetail__billcycle = billCycle)
                    jobCard = JobCard(
                        routeassigned = routeAssignment,
                        consumerdetail = consumerDetails,
                        meterreader = unBilledConsumer.meterreader,
                        reading_month = request.POST.get('billmonth'),
                        is_reading_completed = True,
                        record_status = 'COMPLETED',
                        created_by = request.user.username,
                    )
                    jobCard.save()
                    # save meter reading
                    meterReading = MeterReading(
                        jobcard = jobCard,
                        current_meter_reading = unBilledConsumer.current_meter_reading,
                        image_url = unBilledConsumer.image_url,
                        longitude = unBilledConsumer.longitude,
                        latitude = unBilledConsumer.latitude,
                        reading_date = unBilledConsumer.reading_date,
                        reading_month = request.POST.get('billmonth'),
                        meter_status = meter_status_value,
                        reader_status = reader_status_value,
                        suspicious_activity = unBilledConsumer.suspicious_activity,
                        suspicious_image_url = unBilledConsumer.suspicious_image_url,
                        suspicious_activity_remark = unBilledConsumer.suspicious_activity_remark,
                        comment = unBilledConsumer.comment,
                        comment_v1 = request.POST.get('remark_v1'),
                    )
                    meterReading.save()
                    unBilledConsumer.is_confirmed = True
                    unBilledConsumer.save()
                    unbilledConsumerAssignment.is_confirmed = True
                    unbilledConsumerAssignment.save()
                    unbilledConsumerAssignmentCount.count = unbilledConsumerAssignmentCount.count - 1
                    unbilledConsumerAssignmentCount.save()
                    messages.add_message(request, messages.INFO, 'Reading successfully added.')
                    data = {'success': 'true', 'add':9} # added as reading successfully
                    return HttpResponse(json.dumps(data), content_type='application/json')
                except:
                    unBilledConsumer.bill_cycle_code = request.POST.get('billcycle_code')
                    unBilledConsumer.route_code = request.POST.get('route_id')
                    unBilledConsumer.consumer_no = request.POST.get('consumer_no')
                    unBilledConsumer.meter_no = request.POST.get('meter_no')
                    unBilledConsumer.name = request.POST.get('consumer_name')
                    unBilledConsumer.save()
                    # Route is not yet assigned, Cant add consumer
                    messages.add_message(request, messages.INFO, 'Cant add Reading! Route is not dispatched.')
                    data = {'success': 'true', 'add':1} # 0 for cant add consumer
                    return HttpResponse(json.dumps(data), content_type='application/json')
        else:
            try:

                routeAssignment = RouteAssignment.objects.get(routedetail__route_code = request.POST.get('route_id'), reading_month = request.POST.get('billmonth'), routedetail__billcycle = billCycle)
                jobCard = JobCard(
                    routeassigned = routeAssignment,
                    consumerdetail = consumerDetails,
                    meterreader = unBilledConsumer.meterreader,
                    reading_month = request.POST.get('billmonth'),
                    is_reading_completed = True,
                    record_status = 'COMPLETED',
                    created_by = request.user.username,
                )
                jobCard.save()
                # save meter reading
                meterReading = MeterReading(
                    jobcard = jobCard,
                    current_meter_reading = unBilledConsumer.current_meter_reading,
                    image_url = unBilledConsumer.image_url,
                    longitude = unBilledConsumer.longitude,
                    latitude = unBilledConsumer.latitude,
                    reading_date = unBilledConsumer.reading_date,
                    reading_month = request.POST.get('billmonth'),
                    meter_status = meter_status_value,
                    reader_status = reader_status_value,
                    suspicious_activity = unBilledConsumer.suspicious_activity,
                    suspicious_image_url = unBilledConsumer.suspicious_image_url,
                    suspicious_activity_remark = unBilledConsumer.suspicious_activity_remark,
                    comment = unBilledConsumer.comment,
                    comment_v1 = request.POST.get('remark_v1'),
                )
                meterReading.save()
                unBilledConsumer.is_confirmed = True
                unBilledConsumer.save()
                unbilledConsumerAssignment.is_confirmed = True
                unbilledConsumerAssignment.save()
                unbilledConsumerAssignmentCount.count = unbilledConsumerAssignmentCount.count - 1
                unbilledConsumerAssignmentCount.save()
                messages.add_message(request, messages.INFO, 'Reading successfully added.')
                data = {'success': 'true', 'add':9} # added as duplicate reading successfully
                return HttpResponse(json.dumps(data), content_type='application/json')
            except RouteAssignment.DoesNotExist:
                unBilledConsumer.bill_cycle_code = request.POST.get('billcycle_code')
                unBilledConsumer.route_code = request.POST.get('route_id')
                unBilledConsumer.consumer_no = request.POST.get('consumer_no')
                unBilledConsumer.meter_no = request.POST.get('meter_no')
                unBilledConsumer.name = request.POST.get('consumer_name')
                unBilledConsumer.save()
                # Route is not yet assigned, Cant add consumer
                messages.add_message(request, messages.INFO, 'Cant add Reading! Route is not dispatched.')
                data = {'success': 'true', 'add':1} # 0 for cant add consumer
                return HttpResponse(json.dumps(data), content_type='application/json')
    except ConsumerDetails.DoesNotExist:

        unBilledConsumer.bill_cycle_code = request.POST.get('billcycle_code')
        unBilledConsumer.route_code = request.POST.get('route_id')
        unBilledConsumer.consumer_no = request.POST.get('consumer_no')
        unBilledConsumer.meter_no = request.POST.get('meter_no')
        unBilledConsumer.name = request.POST.get('consumer_name')
        unBilledConsumer.save()
        messages.add_message(request, messages.INFO, 'Cant add Reading! Consumer does not exist! Reading cannot be added. Please regularise the consumer.')
        data = {'success': 'true', 'add':2} # 0 for cant add consumer
        return HttpResponse(json.dumps(data), content_type='application/json')

    data = {'success': 'true'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def dupicatelist(request, billcycle_id = None, month = None):
    billCycle = BillCycle.objects.get(id = billcycle_id)

    meterReading = MeterReading.objects.filter(jobcard__routeassigned__routedetail__billcycle_id = billcycle_id, reading_month = month, is_duplicate = True, is_active = False, is_deleted = False)

    return render(request, 'validationapp/duplicate.html', {'data':meterReading,'billCycle':billCycle, 'month':month, 'monthtoshow':monthhh(month)})


@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def dupicatelist_export(request, billcycle_id = None, month = None):
    try:
        billcycle = BillCycle.objects.get(id = billcycle_id)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="duplicate_readings_' + str(
            billcycle.bill_cycle_code) + '_' + str(month) +  '.csv"';
        writer = csv.writer(response)
        writer.writerow(['RouteID', 'Consumer Number', 'Meter Number', 'Consumer Name', 'Meter Reader Name', 'Current Reading','Date'])

        meterReading = MeterReading.objects.filter(jobcard__routeassigned__routedetail__billcycle_id = billcycle_id, reading_month = month, is_duplicate = True, is_active = False, is_deleted = False)
        for meterReadingOne in meterReading:
            tempList = []
            tempList.append(str(meterReadingOne.jobcard.routeassigned.routedetail.route_code))
            tempList.append(str("'")+str(meterReadingOne.jobcard.consumerdetail.consumer_no).encode('utf-8'))
            tempList.append(meterReadingOne.jobcard.consumerdetail.meter_no)
            tempList.append(meterReadingOne.jobcard.consumerdetail.name)
            tempList.append(meterReadingOne.jobcard.meterreader.first_name + ' ' + meterReadingOne.jobcard.meterreader.last_name)
            tempList.append(meterReadingOne.current_meter_reading)
            tempList.append(meterReadingOne.reading_date)
            writer.writerow(tempList)
        return response
    except Exception, e:
        print e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

# accept this record as a valid reaing record
@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def addduplicate(request):
    meterReading = MeterReading.objects.get(id = request.POST.get('meterreadingid'))
    meterReading.is_duplicate = False
    meterReading.is_active = True
    meterReading.reading_status = 'validation2'
    meterReading.meter_status_v1 = meterReading.meter_status
    meterReading.reader_status_v1 = meterReading.reader_status
    meterReading.comment_v1 = meterReading.comment
    meterReading.current_meter_reading_v1 =meterReading.current_meter_reading
    meterReading.save()
    meterReading.jobcard.is_active = True
    meterReading.jobcard.record_status = 'COMPLETED'
    meterReading.jobcard.save()

    data = {'success': 'true'} # 0 for cant add consumer
    return HttpResponse(json.dumps(data), content_type='application/json')

# reject this reading record
@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def rejectduplicate(request):
    meterReading = MeterReading.objects.get(id = request.POST.get('meterreadingid'))
    meterReading.is_duplicate = True
    meterReading.is_active = False
    meterReading.is_deleted = True
    meterReading.save()
    meterReading.jobcard.is_active = False
    meterReading.jobcard.save()

    data = {'success': 'true'} # 0 for cant add consumer
    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def viewduplicate(request, billcycle_id, month, duplicate_id):
    billCycle = BillCycle.objects.get(id = billcycle_id)
    meter_status_values = MeterStatus.objects.all()
    reader_status_values = ReaderStatus.objects.all()

    meterreading = MeterReading.objects.get(id = duplicate_id)
    route_id = meterreading.jobcard.routeassigned.routedetail.route_code
    formData = {
                    'consumer':meterreading.jobcard.consumerdetail,
                    'meterreading':meterreading,
                    'meterreader':meterreading.jobcard.meterreader,
                }
    return render(request, 'validationapp/viewduplicate.html', {'data':formData,'billCycle':billCycle, 'month':month, 'monthtoshow':monthhh(month),'reader_status_values':reader_status_values, 'meter_status_values':meter_status_values,'route_id':route_id})

@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def validate_consumer_search(request):
    try:
        validatorAssigned = None
        try:
            if request.POST.get('validator') == 1:
                validatorAssigned = ValidatorAssignment.objects.get( ( Q(meterreading__reading_status = 'validation1') | Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )),user = request.user, sent_to_revisit = False, reading_month = request.POST.get('searchmonth'), meterreading__jobcard__consumerdetail__consumer_no = request.POST.get('searchconsumer'), meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False)
            else:
                validatorAssigned = ValidatorAssignment.objects.get( (Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )), user = request.user, sent_to_revisit = False , reading_month = request.POST.get('searchmonth'), meterreading__jobcard__consumerdetail__consumer_no = request.POST.get('searchconsumer') , meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False)
            data = {'success': 'true', 'validator':request.POST.get('validator'), 'month':request.POST.get('searchmonth'), 'billcycleid': validatorAssigned.meterreading.jobcard.routeassigned.routedetail.billcycle_id} # true
            return HttpResponse(json.dumps(data), content_type='application/json')
        except ValidatorAssignment.DoesNotExist:
            data = {'success': 'false'} # false
            return HttpResponse(json.dumps(data), content_type='application/json')

    except Exception,e:
        print e


@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def validator_summery(request, month = None, billcycle_id = None, role = None):
    validators = []
    monthYears = []
    month1 = month
    # get all the bill cycles

    billcyclesArray = []

    billcycle_id_to_pass = None
    role_to_pass = None

    if billcycle_id is not None:
        billcycle_id_to_pass = int(billcycle_id)
    else:
        billcycle_id_to_pass = 0

    if role is not None:
        role_to_pass = int(role)
    else:
        role_to_pass = 0

    billcycles = BillCycle.objects.all()
    for billcycle in billcycles:
        try:
            billschedule = BillSchedule.objects.get(bill_cycle=billcycle, month = month1)
            if billschedule:
                try:
                    billScheduledetail = BillScheduleDetails.objects.get(billSchedule=billschedule, month = month1, last_confirmed = True)
                    billcyclesArray.append(billcycle)
                except:
                    pass
        except:
            pass
    try:
        for month in range(0, SHOW_MONTH):
            date = datetime.date.today() - dateutil.relativedelta.relativedelta(months=month)
            monthYears.append({'value': str(date.year) + checkMonth(date.month),
                               'text': Months[date.month] + ' ' + str(date.year)})

        yearMonth=str(datetime.date.today().year) + checkMonth(datetime.date.today().month)
    except:
        pass
    try:
        meterReadersAsValidator1 = None
        if role_to_pass == 0:
            meterReadersAsValidator1 = UserProfile.objects.filter( ( Q( type = 'VALIDATOR_1') | Q(type = 'VALIDATOR_2') ), status = 'ACTIVE', is_deleted = False)
        elif role_to_pass == 1:
            meterReadersAsValidator1 = UserProfile.objects.filter( type = 'VALIDATOR_1', status = 'ACTIVE', is_deleted = False)
        else:
            meterReadersAsValidator1 = UserProfile.objects.filter( type = 'VALIDATOR_2', status = 'ACTIVE', is_deleted = False)


        for meterReadersAsValidator1One in meterReadersAsValidator1:
            #fetch role of the user
            if billcycle_id_to_pass == 0:
                for billcycle in billcyclesArray:
                    e = None
                    if meterReadersAsValidator1One.type == "VALIDATOR_1":
                        role = 'Validator 1'
                        e = 'validation1'
                    else:
                        role = 'Validator 2'
                        e = 'validation2'

                    # fetch total readings
                    totalAssignedPending = 0
                    totalAssignedCompleted = 0
                    totalAssigned = 0

                    # if meterReadersAsValidator1One.validator.type == "VALIDATOR_1":
                    totalAssigned = ValidatorAssignment.objects.filter(user = meterReadersAsValidator1One, sent_to_revisit = False, reading_month = month1, meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False, meterreading__jobcard__is_active = True, meterreading__jobcard__is_deleted = False, meterreading__jobcard__is_deleted_for_mr = False, meterreading__jobcard__routeassigned__routedetail__billcycle_id = billcycle.id).count()

                    totalAssignedPending = ValidatorAssignment.objects.filter(user = meterReadersAsValidator1One, sent_to_revisit = False, reading_month = month1, meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False, meterreading__jobcard__is_active = True, meterreading__jobcard__is_deleted = False, meterreading__jobcard__is_deleted_for_mr = False, meterreading__jobcard__routeassigned__routedetail__billcycle_id = billcycle.id, meterreading__reading_status = e).count()

                    totalAssignedCompleted = int(totalAssigned) - int(totalAssignedPending)
                    if int(totalAssigned) == 0 and int(totalAssignedCompleted) == 0:
                        pass
                    else:
                        formData = {}
                        formData = {
                                'validator':meterReadersAsValidator1One,
                                'role': role,
                                'totalAssigned':totalAssigned,
                                'totalAssignedCompleted':totalAssignedCompleted,
                                'totalAssignedPending':totalAssignedPending,
                                'billcycle': billcycle.bill_cycle_code,
                                # 'meterreading':meterreading,
                                # 'meterreader':meterreading.jobcard.meterreader,
                            }
                        validators.append(formData)
            else:
                e = None
                if meterReadersAsValidator1One.type == "VALIDATOR_1":
                    role = 'Validator 1'
                    e = 'validation1'
                else:
                    role = 'Validator 2'
                    e = 'validation2'
                # fetch total readings
                totalAssignedPending = 0
                totalAssignedCompleted = 0
                totalAssigned = 0

                totalAssigned = ValidatorAssignment.objects.filter(user = meterReadersAsValidator1One, sent_to_revisit = False, reading_month = month1, meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False, meterreading__jobcard__is_active = True, meterreading__jobcard__is_deleted = False, meterreading__jobcard__is_deleted_for_mr = False, meterreading__jobcard__routeassigned__routedetail__billcycle_id = billcycle_id_to_pass).count()

                totalAssignedPending = ValidatorAssignment.objects.filter(user = meterReadersAsValidator1One, sent_to_revisit = False, reading_month = month1, meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False, meterreading__jobcard__is_active = True, meterreading__jobcard__is_deleted = False, meterreading__jobcard__is_deleted_for_mr = False, meterreading__jobcard__routeassigned__routedetail__billcycle_id = billcycle_id_to_pass, meterreading__reading_status = e).count()


                totalAssignedCompleted = int(totalAssigned) - int(totalAssignedPending)
                if int(totalAssigned) == 0 and int(totalAssignedCompleted) == 0:
                    pass
                else:
                    formData = {}
                    formData = {
                            'validator':meterReadersAsValidator1One,
                            'role': role,
                            'totalAssigned':totalAssigned,
                            'totalAssignedCompleted':totalAssignedCompleted,
                            'totalAssignedPending':totalAssignedPending,
                            'billcycle': (BillCycle.objects.get(id = billcycle_id_to_pass)).bill_cycle_code,
                            # 'meterreading':meterreading,
                            # 'meterreader':meterreading.jobcard.meterreader,
                        }
                    validators.append(formData)
    except Exception, e:
        print 'exception ',str(traceback.print_exc())
    return render(request, 'validationapp/validate_summery1.html', {'monthYears':monthYears,'currentmonth':month1, 'validators':validators, 'billcyclesArray':billcyclesArray, 'billcycle_id_to_pass':billcycle_id_to_pass,'role_to_pass':str(role_to_pass) })


@login_required(login_url='/')
@role_required(privileges=['Validation1','Validation2'],login_url='/',raise_exception=True)
def validator_summery_export(request, month = None, billcycle_id = None, role = None):

    validators = []
    monthYears = []
    month1 = month
    # get all the bill cycles

    billcyclesArray = []

    billcycle_id_to_pass = None
    role_to_pass = None

    if billcycle_id is not None:
        billcycle_id_to_pass = int(billcycle_id)
    else:
        billcycle_id_to_pass = 0

    if role is not None:
        role_to_pass = int(role)
    else:
        role_to_pass = 0

    billcycles = BillCycle.objects.all()
    for billcycle in billcycles:
        try:
            billschedule = BillSchedule.objects.get(bill_cycle=billcycle, month = month1)
            if billschedule:
                try:
                    billScheduledetail = BillScheduleDetails.objects.get(billSchedule=billschedule, month = month1, last_confirmed = True)
                    billcyclesArray.append(billcycle)
                except:
                    pass
        except:
            pass
    try:
        meterReadersAsValidator1 = None
        if role_to_pass == 0:
            meterReadersAsValidator1 = UserProfile.objects.filter( ( Q( type = 'VALIDATOR_1') | Q(type = 'VALIDATOR_2') ), status = 'ACTIVE', is_deleted = False)
        elif role_to_pass == 1:
            meterReadersAsValidator1 = UserProfile.objects.filter( type = 'VALIDATOR_1', status = 'ACTIVE', is_deleted = False)
        else:
            meterReadersAsValidator1 = UserProfile.objects.filter( type = 'VALIDATOR_2', status = 'ACTIVE', is_deleted = False)


        for meterReadersAsValidator1One in meterReadersAsValidator1:
            #fetch role of the user
            if billcycle_id_to_pass == 0:
                for billcycle in billcyclesArray:
                    if meterReadersAsValidator1One.type == "VALIDATOR_1":
                        role = 'Validator 1'
                        totalAssignedAll = ValidatorAssignment.objects.filter((Q(meterreading__reading_status = 'validation1') | Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )),user = meterReadersAsValidator1One, sent_to_revisit = False, reading_month = month1, meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False, meterreading__jobcard__routeassigned__routedetail__billcycle_id = billcycle.id,meterreading__jobcard__is_active = True, meterreading__jobcard__is_deleted = False, meterreading__jobcard__is_deleted_for_mr = False)
                    else:
                        role = 'Validator 2'
                        totalAssignedAll = ValidatorAssignment.objects.filter((Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )),user = meterReadersAsValidator1One, sent_to_revisit = False, reading_month = month1, meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False, meterreading__jobcard__routeassigned__routedetail__billcycle_id = billcycle.id,meterreading__jobcard__is_active = True, meterreading__jobcard__is_deleted = False, meterreading__jobcard__is_deleted_for_mr = False)

                    if totalAssignedAll:
                        for totalAssignedOne in totalAssignedAll:
                            formData = {}
                            formData = {
                                    'meterreader':meterReadersAsValidator1One,
                                    'consumerDetail':totalAssignedOne.meterreading.jobcard.consumerdetail,
                                    'meterreading':totalAssignedOne.meterreading,
                                    'role': role,

                                    # 'meterreading':meterreading,
                                    # 'meterreader':meterreading.jobcard.meterreader,
                                }
                            validators.append(formData)
                    else:
                        pass
            else:
                totalAssignedAll = None

                if meterReadersAsValidator1One.type == "VALIDATOR_1":
                    role = 'Validator 1'
                    totalAssignedAll = ValidatorAssignment.objects.filter((Q(meterreading__reading_status = 'validation1') | Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )),user = meterReadersAsValidator1One, sent_to_revisit = False, reading_month = month1, meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False, meterreading__jobcard__routeassigned__routedetail__billcycle_id = billcycle_id_to_pass,meterreading__jobcard__is_active = True, meterreading__jobcard__is_deleted = False, meterreading__jobcard__is_deleted_for_mr = False)
                else:
                    role = 'Validator 2'
                    totalAssignedAll = ValidatorAssignment.objects.filter((Q(meterreading__reading_status = 'validation2')| Q(meterreading__reading_status = 'complete' )),user = meterReadersAsValidator1One, sent_to_revisit = False, reading_month = month1, meterreading__is_deleted = False, meterreading__is_active = True, meterreading__is_duplicate = False, meterreading__jobcard__routeassigned__routedetail__billcycle_id = billcycle_id_to_pass,meterreading__jobcard__is_active = True, meterreading__jobcard__is_deleted = False, meterreading__jobcard__is_deleted_for_mr = False)

                if totalAssignedAll:
                    for totalAssignedOne in totalAssignedAll:
                        formData = {
                                'meterreader':meterReadersAsValidator1One,
                                'consumerDetail':totalAssignedOne.meterreading.jobcard.consumerdetail,
                                'meterreading':totalAssignedOne.meterreading,
                                'role': role,
                            }
                        validators.append(formData)
                else:
                    pass

    except Exception, e:
        print 'exception ',str(traceback.print_exc())

    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="validator_summery' + str(
            month) + '.csv"';
        writer = csv.writer(response)
        writer.writerow(
            ['BILL_CYC_CD','BILL_MONTH','ROUTE_CODE','CONSUMER_NO','CONSUMER_NAME','METER_NO',
            'READING_STATUS','CURRENT_MT_READING','CURRENT_MT_RDG_V1','CURRENT_MT_RDG_V2','METER_STS',
             'METER_STS_V1','METER_STS_V2','READER_STS','READER_STS_V1','READER_STS_V2','REMARK',
             'REMARK_V1','REMARK_V2','IMG_REMARK_V1','IMG_REMARK_V2','VALIDATOR1_DATE','VALIDATOR2_DATE',
             'VALIDATOR1_NAME','VALIDATOR2_NAME'])

        for validator in validators:
            consumerDetail = validator['consumerDetail']
            reading_status = validator['meterreading']
            tempList = []

            tempList.append(consumerDetail.bill_cycle.bill_cycle_code)
            tempList.append(consumerDetail.bill_month)
            tempList.append(consumerDetail.route.route_code)
            tempList.append("'" + str(consumerDetail.consumer_no))
            tempList.append(consumerDetail.name)
            tempList.append(consumerDetail.meter_no)


            if reading_status:
                tempList.append(reading_status.reading_status)
            else:
                tempList.append('Not Taken')

            if reading_status:
                tempList.append(reading_status.current_meter_reading if reading_status.current_meter_reading else '----')
                tempList.append(reading_status.current_meter_reading_v1 if reading_status.current_meter_reading_v1 else '----')
                tempList.append(reading_status.current_meter_reading_v2 if reading_status.current_meter_reading_v2 else '----')
            else:
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')

            if reading_status:
                try:
                    tempList.append(reading_status.meter_status.meter_status)
                except Exception:
                    tempList.append('----')
                try:
                    tempList.append(reading_status.meter_status_v1.meter_status)
                except Exception:
                    tempList.append('----')
                try:
                    tempList.append(reading_status.meter_status_v2.meter_status)
                except Exception:
                    tempList.append('----')
            else:
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')


            if reading_status:
                try:
                    tempList.append(reading_status.reader_status.reader_status)
                except Exception:
                    tempList.append('----')
                try:
                    tempList.append(reading_status.reader_status_v1.reader_status)
                except Exception:
                    tempList.append('----')
                try:
                    tempList.append(reading_status.reader_status_v2.reader_status)
                except Exception:
                    tempList.append('----')
            else:
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')

            if reading_status:
                try:
                    tempList.append('----' if(reading_status.comment is None or reading_status.comment == '') else reading_status.comment )
                except:
                    tempList.append('----')
                try:
                    tempList.append('----' if(reading_status.comment_v1 is None or reading_status.comment_v1 == '') else reading_status.comment_v1)
                except:
                    tempList.append('----')
                try:
                    tempList.append('----' if(reading_status.comment_v2 is None or reading_status.comment_v2 == '') else reading_status.comment_v2)
                except:
                    tempList.append('----')
                try:
                    tempList.append(reading_status.image_remark_v1 if (reading_status.image_remark_v1 is not None or reading_status.image_remark_v1 is not '') else '----')
                except:
                    tempList.append('----')
                try:
                    tempList.append(reading_status.image_remark_v2 if (reading_status.image_remark_v2 is not None or reading_status.image_remark_v2 is not '') else '----')
                except:
                    tempList.append('----')

            else:
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')

            if reading_status:
                if reading_status.validated_on_v1:
                    tempList.append(reading_status.validated_on_v1.strftime("%d/%m/%Y"))
                else:
                    tempList.append('----')

                if reading_status.validated_on_v2:
                    tempList.append(reading_status.validated_on_v2.strftime("%d/%m/%Y"))
                else:
                    tempList.append('----')

            else:
                tempList.append('----')
                tempList.append('----')

            if reading_status:
                if reading_status.updated_by_v1:
                    tempList.append(reading_status.updated_by_v1.first_name+' '+reading_status.updated_by_v1.last_name)
                else:
                    tempList.append('---')

                if reading_status.updated_by_v2:
                    tempList.append(reading_status.updated_by_v2.first_name+' '+reading_status.updated_by_v2.last_name)
                else:
                    tempList.append('---')
            else:
                tempList.append('---')
                tempList.append('---')

            writer.writerow(tempList)

        return response
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|upload.py|get_reading_list', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')
