import django
from django.db import models
from django.contrib.auth.models import User
from celery.decorators import task
from django.conf import settings
import traceback
import datetime
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from adminapp.models import RouteDetail,UserProfile, Availability
from dispatch.models import RouteAssignment,JobCard, RouteDeassigned, ValidatorAssignmentCount, ValidatorAssignment, MeterReading, UnbilledConsumerAssignmentCount, UnbilledConsumerAssignment,RouteProcess
from scheduleapp.models import BillSchedule,BillScheduleDetails
from consumerapp.models import ConsumerDetails, UnBilledConsumers
from meterreaderapp.models import PreferredBillCycle
from django.db.models import Q


@task(name="aysnc-assign-mr")
def aysnc_assign_mr(mr_id,route_id, current_month):
    try:
        today = datetime.date.today()
    	route = RouteDetail.objects.get(id=route_id, bill_month = current_month)
    	billschedule = BillSchedule.objects.get(bill_cycle=route.billcycle, month = current_month)
    	billscheduledetail=BillScheduleDetails.objects.get(billSchedule=billschedule, month = current_month,last_confirmed=True)
        routeassignment = None
        try:
            routeassignment = RouteAssignment.objects.get(routedetail = route, reading_month = current_month)
        except:
            pass

        if routeassignment:
            jobcards = JobCard.objects.filter(routeassigned = routeassignment, is_reading_completed = False, is_active = True, is_deleted = False, is_revisit = False)
            for jobcard in jobcards:
                if jobcard.meterreader is not None:
                    jobcard.is_active = False
                    jobcard.is_deleted = True
                    jobcard.record_status = 'REASSIGNED'
                    jobcard.updated_by = 'admin'
                    jobcard.Updated_on = today
                    jobcard.save()
                    jobcardNew = JobCard(
                        routeassigned = routeassignment,
                        consumerdetail = jobcard.consumerdetail,
                        meterreader_id = mr_id,
                        completion_date = jobcard.completion_date,
                        reading_month = current_month,
                        created_by = 'admin',
                    )
                    jobcardNew.save()
                else:
                    jobcard.meterreader_id = mr_id
                    jobcard.updated_by = 'admin'
                    jobcard.updated_on = today
                    jobcard.save()

            if routeassignment.meterreader is not None:
                routeDeassigned = RouteDeassigned(routedetail = routeassignment.routedetail,
                meterreader = routeassignment.meterreader,
                deassign_date = today)
                routeDeassigned.save()
            routeassignment.meterreader_id = mr_id
            routeassignment.is_active = True
            routeassignment.dispatch_status = 'Started'
            routeassignment.updated_by = 'admin'
            routeassignment.updated_on = today
            routeassignment.save()
        else:
            routeassignment = RouteAssignment(
            	routedetail = route,
            	meterreader_id = mr_id,
            	assign_date = today,
            	due_date = billscheduledetail.end_date,
            	reading_month = current_month,
                dispatch_status = 'Started',
                is_active = True,
                sent_to_mr = True,
            	created_by = 'admin',
            	)
            routeassignment.save()
            consumerdetails = ConsumerDetails.objects.filter(route=route, bill_month = current_month)
            for consumerdetail in consumerdetails:
                jobcard = JobCard(
                    routeassigned = routeassignment,
                    consumerdetail = consumerdetail,
                    meterreader_id = mr_id,
                    completion_date = billscheduledetail.end_date,
                    reading_month = current_month,
                    is_active = True,
                    created_by = 'admin',
                )
                jobcard.save()
        routeProcess=RouteProcess.objects.get(routedetail__id=route_id,reading_month=current_month)
        routeProcess.is_processing=False
        routeProcess.save()
    except Exception, e:
        routeProcess=RouteProcess.objects.get(routedetail__id=route_id,reading_month=current_month)
        routeProcess.is_processing=False
        routeProcess.save()
    return

@task(name="aysnc-deassign-mr")
def aysnc_deassign_mr(route_id, current_month):
    try:
        jobcardss=''
        today = datetime.date.today()
        route = RouteDetail.objects.get(id=route_id, bill_month = current_month)
        # billschedule = BillSchedule.objects.get(bill_cycle=route.billcycle)
        # billscheduledetail=BillScheduleDetails.objects.get(billSchedule=billschedule)
        routeassignment = RouteAssignment.objects.get(routedetail = route,reading_month=current_month,is_active = True)

        jobcards = JobCard.objects.filter(routeassigned = routeassignment, is_reading_completed = False, is_deleted = False, is_active = True,is_revisit=False)
        try:
            jobcardss = JobCard.objects.filter(routeassigned__routedetail = route_id, is_reading_completed = True, is_deleted = False, is_active = True)
            if jobcardss:
                routeassignment.dispatch_status='Partial'
                routeassignment.save()
            else:
                routeassignment.dispatch_status='Not Dispatched'
                routeassignment.save()
                pass
        except:
            pass

        for jobcard in jobcards:
            jobcard.updated_by = 'admin'
            jobcard.is_deleted = True
            jobcard.is_active = False
            jobcard.record_status = 'DEASSIGNED'
            jobcard.Updated_on = today
            jobcard.save()

            jobcardNew = JobCard(
                routeassigned = routeassignment,
                consumerdetail = jobcard.consumerdetail,
                completion_date = jobcard.completion_date,
                reading_month = current_month,
                created_by = 'admin',
                is_active = True
            )
            jobcardNew.save()

        routeDeassigned = RouteDeassigned(routedetail = routeassignment.routedetail,
            meterreader = routeassignment.meterreader,
            deassign_date = today)
        routeDeassigned.save()

        routeassignment.meterreader = None
        routeassignment.is_active = False
        updated_by = 'admin'
        updated_on = today
        routeassignment.save()

        routeProcess=RouteProcess.objects.get(routedetail__id=route_id,reading_month=current_month)
        routeProcess.is_processing=False
        routeProcess.save()

    except Exception, e:
        print "An unexpected error occured !!"

        routeProcess=RouteProcess.objects.get(routedetail__id=route_id,reading_month=current_month)
        routeProcess.is_processing=False
        routeProcess.save()
    return

# PreferredBillCycle
@periodic_task(run_every=datetime.timedelta(minutes=1),name="allocate_validate_mr",ignore_result=True)
def allocate_validate_mr():
    try:
        currentmonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month )

        userProfiles = UserProfile.objects.filter( (Q(type = 'VALIDATOR_1') |Q(type = 'VALIDATOR_2')), status = 'ACTIVE', is_deleted = False)
        for userProfile in userProfiles:
            try:
                validatorAssignmentCount = ValidatorAssignmentCount.objects.get(user = userProfile)
            except ValidatorAssignmentCount.DoesNotExist:
                validatorAssignmentCreate = ValidatorAssignmentCount(user = userProfile,count = 0)
                validatorAssignmentCreate.save()
                pass
        # Assignment for validator1
        validatorAssignmentCount = None


        meterReadersAsValidator1 = Availability.objects.filter(available = 'AVAILABLE', validator__type = 'VALIDATOR_1', validator__status = 'ACTIVE', validator__is_deleted = False)

        meterReadings = None
        meterReadings = MeterReading.objects.filter(reading_status = 'validation1', is_assigned_to_v1 = False, is_deleted = False, is_active = True, is_duplicate = False)
        if meterReadings:
            for meterReading in meterReadings:
                found = False
                for meterReadersAsValidator1One in meterReadersAsValidator1:
                    preferredBillCycle = PreferredBillCycle.objects.filter(user_id = meterReadersAsValidator1One.validator.id, bill_cycle_code = meterReading.jobcard.routeassigned.routedetail.billcycle.bill_cycle_code)
                    if preferredBillCycle:
                        try:
                            validatorAssignmentCount = ValidatorAssignmentCount.objects.get(count__lt =  101, user = meterReadersAsValidator1One.validator)

                            validatorAssignment = ValidatorAssignment(user = meterReadersAsValidator1One.validator,meterreading = meterReading,created_by = 'Admin', assigned_to = 'validator1', reading_month = meterReading.reading_month)
                            validatorAssignment.save()
                            validatorAssignmentCount.count = validatorAssignmentCount.count + 1
                            validatorAssignmentCount.save()
                            meterReading.is_assigned_to_v1 = True
                            meterReading.save()
                            found = True
                            break
                        except Exception, e:
                            pass
                    else:
                        pass
                if found == False:
                    for meterReadersAsValidator1One in meterReadersAsValidator1:
                        preferredBillCycle = PreferredBillCycle.objects.filter(user_id = meterReadersAsValidator1One.validator.id, bill_cycle_code = 'All')
                        if preferredBillCycle:
                            try:
                                validatorAssignmentCount = ValidatorAssignmentCount.objects.get(count__lt =  101, user = meterReadersAsValidator1One.validator)

                                validatorAssignment = ValidatorAssignment(user = meterReadersAsValidator1One.validator,meterreading = meterReading,created_by = 'Admin', assigned_to = 'validator1', reading_month = meterReading.reading_month)
                                validatorAssignment.save()
                                validatorAssignmentCount.count = validatorAssignmentCount.count + 1
                                validatorAssignmentCount.save()
                                meterReading.is_assigned_to_v1 = True
                                meterReading.save()
                                break
                            except Exception, e:
                                pass

        # Assignment for validator2
        validatorAssignmentCount = None
        meterReadersAsValidator2 = Availability.objects.filter(available = 'AVAILABLE', validator__type = 'VALIDATOR_2', validator__status = 'ACTIVE', validator__is_deleted = False)
        meterReadings = None
        meterReadings = MeterReading.objects.filter(reading_status = 'validation2', is_assigned_to_v2 = False, is_deleted = False, is_active = True, is_duplicate = False)
        if meterReadings:
            for meterReading in meterReadings:
                found = False
                for meterReadersAsValidator2One in meterReadersAsValidator2:
                    preferredBillCycle = PreferredBillCycle.objects.filter(user_id = meterReadersAsValidator2One.validator.id, bill_cycle_code = meterReading.jobcard.routeassigned.routedetail.billcycle.bill_cycle_code)
                    if preferredBillCycle:
                        try:
                            validatorAssignmentCount = ValidatorAssignmentCount.objects.get(count__lt =  101, user = meterReadersAsValidator2One.validator)
                            validatorAssignment = ValidatorAssignment(user = meterReadersAsValidator2One.validator,meterreading = meterReading,created_by = 'Admin', assigned_to = 'validator2', reading_month = meterReading.reading_month)
                            validatorAssignment.save()
                            validatorAssignmentCount.count = validatorAssignmentCount.count + 1
                            validatorAssignmentCount.save()
                            meterReading.is_assigned_to_v2 = True
                            meterReading.save()
                            found = True
                            break
                        except:
                            pass
                    else:
                        pass
                if found == False:
                    for meterReadersAsValidator2One in meterReadersAsValidator2:
                        preferredBillCycle = PreferredBillCycle.objects.filter(user_id = meterReadersAsValidator2One.validator.id, bill_cycle_code = 'All')
                        if preferredBillCycle:
                            try:
                                validatorAssignmentCount = ValidatorAssignmentCount.objects.get(count__lt =  101, user = meterReadersAsValidator2One.validator)
                                validatorAssignment = ValidatorAssignment(user = meterReadersAsValidator2One.validator,meterreading = meterReading,created_by = 'Admin', assigned_to = 'validator2', reading_month = meterReading.reading_month)
                                validatorAssignment.save()
                                validatorAssignmentCount.count = validatorAssignmentCount.count + 1
                                validatorAssignmentCount.save()
                                meterReading.is_assigned_to_v2 = True
                                meterReading.save()
                                break
                            except:
                                pass

        print 'allocate_validate_mr Completed'
    except Exception, e:
        print e
    return

@periodic_task(run_every=datetime.timedelta(minutes=1),name="allocate_unbilled_consumers",ignore_result=True)
def allocate_unbilled_consumers():
    userProfiles = UserProfile.objects.filter( type = 'VALIDATOR_1', status = 'ACTIVE', is_deleted = False)
    for userProfile in userProfiles:
        try:
            unbilledConsumerAssignmentCount = UnbilledConsumerAssignmentCount.objects.get(user = userProfile)
        except UnbilledConsumerAssignmentCount.DoesNotExist:
            unbilledConsumerAssignmentCountCreate = UnbilledConsumerAssignmentCount(user = userProfile,count = 0)
            unbilledConsumerAssignmentCountCreate.save()
            pass

    unbilledConsumerAssignmentCount = None
    meterReadersAsValidator1 = UserProfile.objects.filter( type = 'VALIDATOR_1', status = 'ACTIVE', is_deleted = False)
    unbilledConsumers = None
    unbilledConsumers = UnBilledConsumers.objects.filter(is_assigned =False, is_confirmed = False)
    if unbilledConsumers:
        for unbilledConsumer in unbilledConsumers:
            for meterReadersAsValidator1One in meterReadersAsValidator1:
                try:
                    unbilledConsumerAssignmentCount = UnbilledConsumerAssignmentCount.objects.get(count__lt =  101, user = meterReadersAsValidator1One)

                    unbilledConsumerAssignment = UnbilledConsumerAssignment(user = meterReadersAsValidator1One,unbillconsumer = unbilledConsumer,reading_month = unbilledConsumer.reading_month, created_by = 'Admin')
                    unbilledConsumerAssignment.save()
                    unbilledConsumerAssignmentCount.count = unbilledConsumerAssignmentCount.count + 1
                    unbilledConsumerAssignmentCount.save()
                    unbilledConsumer.is_assigned = True
                    unbilledConsumer.save()
                    break
                except Exception, e:
                    pass

    print 'allocate_unbilled_consumers Completed'

def checkMonth(month):
    if month > 9:
        return str(month)
    else:
        return '0' + str(month)


@task(name="aysnc-assign-mr-revisit")
def aysnc_assign_mr_revisit(mr_id,route_id, current_month):
    try:
        route = RouteDetail.objects.get(id=route_id, bill_month = current_month)
        billschedule = BillSchedule.objects.get(bill_cycle=route.billcycle, month = current_month)
        billscheduledetail=BillScheduleDetails.objects.get(billSchedule=billschedule, month = current_month,last_confirmed=True)
        endDate = billscheduledetail.end_date
        routeassignment = None
        try:
            routeassignment = RouteAssignment.objects.get(routedetail = route, reading_month = current_month)
            try:
                jobCardAll = JobCard.objects.filter(meterreader = None, is_active = True, is_revisit = True,routeassigned=routeassignment)
                for jobCardOne in jobCardAll:
                # print request.user.username
                    jobCardOne.meterreader_id = mr_id
                    jobCardOne.updated_by= 'admin',
                    jobCardOne.save()
            except Exception:
                 pass

            routeProcess=RouteProcess.objects.get(routedetail__id=route_id,reading_month=current_month)
            routeProcess.is_processing=False
            routeProcess.save()

        except:
            routeProcess=RouteProcess.objects.get(routedetail__id=route_id,reading_month=current_month)
            routeProcess.is_processing=False
            routeProcess.save()
            pass

    except:
        routeProcess=RouteProcess.objects.get(routedetail__id=route_id,reading_month=current_month)
        routeProcess.is_processing=False
        routeProcess.save()
        pass
    return

@task(name="aysnc-assign-mr-revisit-list")
def aysnc_assign_mr_revisit_list(mr_id,route_id, current_month,jobcard_id):
    try:
        today = datetime.date.today()
        route = RouteDetail.objects.get(id=route_id, bill_month = current_month)
        billschedule = BillSchedule.objects.get(bill_cycle=route.billcycle, month = current_month)
        billscheduledetail=BillScheduleDetails.objects.get(billSchedule=billschedule, month = current_month,last_confirmed=True)
        routeassignment = None
        try:
            routeassignment = RouteAssignment.objects.get(routedetail = route, reading_month = current_month)
        except:
            pass

        jobcard = JobCard.objects.get(id=jobcard_id)
        if jobcard.meterreader is not None:
            jobcard.is_active = False
            jobcard.is_deleted = True
            jobcard.record_status = 'REASSIGNED'
            jobcard.updated_by = 'admin'
            jobcard.Updated_on = today
            jobcard.save()
            jobcardNew = JobCard(
                routeassigned = routeassignment,
                consumerdetail = jobcard.consumerdetail,
                meterreader_id = mr_id,
                completion_date = jobcard.completion_date,
                is_revisit =True,
                reading_month = current_month,
                created_by = 'admin',
            )
            jobcardNew.save()
        else:
            jobcard.meterreader_id = mr_id
            jobcard.updated_by = 'admin'
            jobcard.updated_on = today
            jobcard.save()
    except Exception,e:
        print e
        pass
    return



@task(name="aysnc-deassign-mr-revisit")
def aysnc_deassign_mr_revisit(route, bill_month,jobcard_id):
    try:
        today = datetime.date.today()
        route = RouteDetail.objects.get(id=route, bill_month = bill_month)
        routeassignment = RouteAssignment.objects.get(routedetail = route,reading_month=bill_month)
        jobcard = JobCard.objects.get(id=jobcard_id)
        jobcard.updated_by = 'admin'
        jobcard.is_deleted = True
        jobcard.is_active = False
        jobcard.record_status = 'DEASSIGNED'
        jobcard.Updated_on = today
        jobcard.save()
        jobcardNew = JobCard(

            routeassigned = routeassignment,
            consumerdetail = jobcard.consumerdetail,
            completion_date = jobcard.completion_date,
            reading_month = bill_month,
            is_revisit = True,
            created_by = 'admin',
            is_active = True
        )
        jobcardNew.save()

    except Exception, e:
        print e
        print "An unexpected error occured !!"
    return
