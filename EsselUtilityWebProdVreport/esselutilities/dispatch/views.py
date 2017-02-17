__author__ = 'Vijay/Shubham'
import csv
import json
import pdb
import smtplib
import base64
import pdb
from time import timezone
import datetime
import django
import logging
from django.shortcuts import render
from dispatch.models import MeterStatus,RouteAssignment,JobCard,ReaderStatus,MeterReading,RouteProcess
from scheduleapp.models import BillSchedule,PN33Download,BillScheduleDetails
from authenticateapp.decorator import role_required
from adminapp.models import State,City,Utility,EmployeeType,UserProfile,UserPrivilege,UserRole,BillCycle,RouteDetail,Availability
from consumerapp.models import ConsumerDetails
from meterreaderapp.models import DeviceDetail,PreferredRoutes
from django.contrib.auth.decorators import login_required
from django.db.models import Q
# Create your views here.
from adminapp.constraints import SHOW_MONTH
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from dispatch.tasks import aysnc_assign_mr, aysnc_deassign_mr, aysnc_assign_mr_revisit,aysnc_assign_mr_revisit_list,aysnc_deassign_mr_revisit

import dateutil.relativedelta

privileges=['Dashboard','Import PN33','Schedule','Dispatch','Validation1','Validation2','Approve schedule','Upload','System User','Administration']
log = logging.getLogger(__name__)


Month = {
    '01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR',
    '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AUG',
    '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'}


Months = {
    1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR',
    5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG',
    9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'}



FILTER_BY=[{'value':'All','text':'All'},
           {'value':'1','text':'Today'},
           {'value':'2','text':'Tomorrow'}]


def monthhh(yearMonth):
    try:
        return Month[yearMonth[-2:]]
    except Exception, e:
        print 'Exception|billCycleFilter|month', e
        return None



def checkMonth(month):
    if month > 9:
        return str(month)
    else:
        return '0' + str(month)


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def view_jobcard(request, month = None):
    data={}
    finallist=[]
    objlist={}
    completed=0
    pending=0
    revisitcase=''
    count=0
    routedispatched=None
    totalreading=None
    totalconsumer=0
    readindingcompletedstatus=False
    incomplete=0
    totalbillcycle = 0
    currentmonth = None
    totalbillcycle=0
    Notstrted=0
    notstared=False


    if month:
        currentmonth = month
    else:
        currentmonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month )

    try:
        monthYears = []
        for month in range(0, SHOW_MONTH):
            date = datetime.date.today() - dateutil.relativedelta.relativedelta(months=month)
            monthYears.append({'value': str(date.year) + checkMonth(date.month),
                               'text': Months[date.month] + ' ' + str(date.year)})

        yearMonth=str(datetime.date.today().year) + checkMonth(datetime.date.today().month)
    except:
        pass

    filter_date = datetime.date.today()
    try:
        billcycles =BillCycle.objects.filter().order_by('bill_cycle_code')
        for billcycle in billcycles:
            readindingcompletedstatus=False
            try:
                is_schedule_completed=False
                billschedules = BillSchedule.objects.get(bill_cycle=billcycle, month = currentmonth,is_deleted=False)
                if billschedules.is_uploaded:
                    is_schedule_completed=True
                else:
                  pass
                try:
                    billScheduledetail=BillScheduleDetails.objects.get(billSchedule=billschedules, month = currentmonth,last_confirmed=True,end_date__lt=filter_date)
                    is_schedule_completed=True
                except:
                  pass
                pn33downloads = PN33Download.objects.get(bill_schedule=billschedules, month = currentmonth,download_status='Completed')
                if pn33downloads:
                    totalbillcycle=totalbillcycle + 1

                    monthh=monthhh(billschedules.month)
                    totalConsumers = ConsumerDetails.objects.filter(bill_cycle=billcycle, bill_month = currentmonth)
                    totalConsumer=len(totalConsumers)
                    route=RouteDetail.objects.filter(billcycle=billcycle, bill_month = currentmonth)
                    totalroutes =len(RouteDetail.objects.filter(billcycle=billcycle, bill_month = currentmonth,is_deleted=False))

                    try:
                        routedispatched=len(RouteAssignment.objects.filter(routedetail__billcycle=billcycle,sent_to_mr=True,is_deleted=False, reading_month = currentmonth,is_active=True))
                        isdispatched=False
                        notstared=False
                        if is_schedule_completed or billschedules.is_uploaded:
                            completed=completed+1

                        elif routedispatched < 1:
                            notstared=True
                            Notstrted=Notstrted+1


                        elif routedispatched==totalroutes:
                            isdispatched=True
                            readindingcompletedstatus=False
                            total=len(JobCard.objects.filter(routeassigned__routedetail__billcycle=billcycle,is_deleted=False,is_active=True,reading_month = currentmonth))
                            totalMeterReadingCompleted = MeterReading.objects.filter(jobcard__routeassigned__routedetail__billcycle=billcycle, reading_status='complete', reading_month = currentmonth,is_deleted=False)
                            totalreading=len(totalMeterReadingCompleted)
                            if totalreading==total:
                              completed=completed+1
                              readindingcompletedstatus=True
                              isdispatched=False
                            else:
                                readindingcompletedstatus=False
                                incomplete=incomplete+1

                        else:
                         pending=pending+1
                    except:
                      pass

            except:
                pass

            try:
                revisitcase=False
                revisit=MeterReading.objects.filter(jobcard__routeassigned__routedetail__billcycle=billcycle,reading_status='revisit', reading_month = currentmonth)
                if revisit:
                    revisitcase=True

            except Exception,e:
              pass

            try:
                billschedules = BillSchedule.objects.get(bill_cycle=billcycle, month = currentmonth,is_deleted=False)
                billScheduledetail=BillScheduleDetails.objects.get(billSchedule=billschedules,month = currentmonth,last_confirmed=True)
                pn33downloads = PN33Download.objects.get(bill_schedule=billschedules, month = currentmonth,download_status='Completed')
                if pn33downloads:
                   totalroutes = RouteDetail.objects.filter(billcycle=billcycle, bill_month = currentmonth,is_deleted=False)
                   totalconsumer = ConsumerDetails.objects.filter(bill_cycle=billcycle, bill_month = currentmonth)

                   objlist = {
                    'bill_cycle_name':billcycle.bill_cycle_name,
                    'billcycle': billschedules,
                    'startdate': billScheduledetail.start_date.strftime('%d/%m/%Y'),
                    'enddate': billScheduledetail.end_date.strftime('%d/%m/%Y'),
                    'totalroutes': len(totalroutes),
                    'totalconsumer': len(totalconsumer),
                    'revisitcase':revisitcase,
                    'isdispatched':isdispatched,
                    'readindingcompletedstatus':readindingcompletedstatus,
                    'month':monthh,
                    'is_schedule_completed':is_schedule_completed,
                    'notstared':notstared,
                    }
                   finallist.append(objlist)
                else:
                  pass

            except Exception as e:
                pass

        data = {'finallist': finallist,'totalbillcycle':totalbillcycle,'Filters':FILTER_BY,'completed':completed,'pending':pending,'incomplete':incomplete,'monthYears':monthYears, 'currentmonth' : currentmonth,'Notstrted':Notstrted}
    except Exception as e:

        data = {'monthYears':monthYears,  'currentmonth' : currentmonth }
    return render(request, 'dispatch/dispatch.html', data)


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
@csrf_exempt

def filter_jobcard(request):
    day=request.POST.get('filterBy')
    currentmonth = request.POST.get('currentmonth')
    data=[]
    finallist=[]
    readindingcompletedstatus=False
    Notstrted=0
    notstared=False
    print 'Request in with---', request.POST
    filter_date = datetime.date.today() + datetime.timedelta(days=int(1))
    billcycles =BillCycle.objects.filter().order_by('bill_cycle_code')
    for billcycle in billcycles:
        try:
            PN33Downloads=PN33Download.objects.filter(bill_schedule__bill_cycle=billcycle,month = currentmonth,download_status='Completed',is_deleted=False)
            for pn33download in PN33Downloads:
                try:
                    if day!='All':
                       filter_date_today = datetime.date.today()
                       is_schedule_completed=False
                       billScheduledetails = BillScheduleDetails.objects.filter(billSchedule=pn33download.bill_schedule,start_date=filter_date,month=currentmonth,last_confirmed=True)
                       for billScheduledetail in billScheduledetails:
                           if billScheduledetail.billSchedule.is_uploaded:
                              is_schedule_completed=True
                           else:
                            pass
                           try:
                              is_schedule_completed=False
                              billSchedule = BillScheduleDetails.objects.get(billSchedule=pn33download.bill_schedule,start_date=filter_date,month=currentmonth,last_confirmed=True,end_date__lt=filter_date_today)
                              is_schedule_completed=True
                           except:
                            pass
                           reading_month=billScheduledetail.month
                           monthh=monthhh(billScheduledetail.month)
                           totalroute = RouteDetail.objects.filter(billcycle=billScheduledetail.billSchedule.bill_cycle.id, bill_month = currentmonth)
                           totalroutes = len(totalroute)
                           totalconsumer = ConsumerDetails.objects.filter(bill_cycle=billScheduledetail.billSchedule.bill_cycle.id, bill_month = currentmonth)
                           countconsumer = len(totalconsumer)
                           try:
                              isdispatched=False
                              routedispatched=len(RouteAssignment.objects.filter(routedetail__billcycle=billScheduledetail.billSchedule.bill_cycle.id,sent_to_mr=True,is_deleted=False, reading_month = currentmonth,is_active=True))

                              if is_schedule_completed or pn33download.bill_schedule.is_uploaded:
                                    completed=completed+1
                                    is_schedule_completed=True
                              elif routedispatched < 1:
                                  notstared=True
                                  Notstrted=Notstrted+1


                              elif routedispatched==totalroutes:
                                  isdispatched=True
                                  readindingcompletedstatus=False
                                  total=len(JobCard.objects.filter(routeassigned__routedetail__billcycle=billcycle,is_deleted=False,is_active=True,reading_month = currentmonth))
                                  totalMeterReadingCompleted = MeterReading.objects.filter(jobcard__routeassigned__routedetail__billcycle=billScheduledetail.billSchedule.bill_cycle.id, reading_status='complete', reading_month = currentmonth,is_deleted=False)
                                  totalreading=len(totalMeterReadingCompleted)
                                  if totalreading==total:
                                    completed=completed+1
                                    readindingcompletedstatus=True
                                    isdispatched=False
                                    incomplete=incomplete-1
                                  else:
                                      readindingcompletedstatus=False
                                      incomplete=incomplete+1

                              else:
                               pending=pending+1
                           except:
                              pass
                           objlist = {
                            'bill_cycle_name':billScheduledetail.billSchedule.bill_cycle.bill_cycle_name,
                            'billcycle':billScheduledetail.billSchedule.bill_cycle,
                            'startdate': billScheduledetail.start_date.strftime('%d/%m/%Y'),
                            'enddate': billScheduledetail.end_date.strftime('%d/%m/%Y'),
                            'totalroutes': len(totalroute),
                            'totalconsumer': len(totalconsumer),
                            'readindingcompletedstatus':readindingcompletedstatus,
                            'isdispatched':isdispatched,
                            'currentmonth':reading_month,
                            'month':monthh,
                            'is_schedule_completed':is_schedule_completed,
                            'Notstrted':Notstrted,
                            'notstared':notstared,
                             }

                           finallist.append(objlist)
                           data={'finallist':finallist}
                    else:
                     filter_date_today = datetime.date.today()
                     billScheduledetails = BillScheduleDetails.objects.filter(billSchedule=pn33download.bill_schedule,month=currentmonth,last_confirmed=True)
                     for billScheduledetail in billScheduledetails:
                         try:
                              is_schedule_completed=False
                              if billScheduledetail.billSchedule.is_uploaded:
                                is_schedule_completed=True
                              else:
                                pass
                              billSchedule = BillScheduleDetails.objects.get(billSchedule=pn33download.bill_schedule,month=currentmonth,last_confirmed=True,end_date__lt=filter_date_today)
                              is_schedule_completed=True
                         except:
                              pass
                         reading_month=billScheduledetail.month
                         monthh=monthhh(billScheduledetail.month)
                         totalroute = RouteDetail.objects.filter(billcycle=billScheduledetail.billSchedule.bill_cycle.id,bill_month=reading_month)
                         totalroutes=len(totalroute)
                         totalconsumer = ConsumerDetails.objects.filter(bill_cycle=billScheduledetail.billSchedule.bill_cycle.id, bill_month = reading_month)
                         countconsumer = len(totalconsumer)
                         try:
                            isdispatched=False
                            notstared=False
                            routedispatched=len(RouteAssignment.objects.filter(routedetail__billcycle=billScheduledetail.billSchedule.bill_cycle.id,sent_to_mr=True,is_deleted=False, reading_month = currentmonth,is_active=True))
                            if is_schedule_completed or billScheduledetail.billSchedule.is_uploaded:
                                completed=completed+1
                                is_schedule_completed=True
                            elif routedispatched < 1:
                                notstared=True
                                Notstrted=Notstrted+1

                            elif routedispatched==totalroutes:
                                isdispatched=True
                                readindingcompletedstatus=False
                                total=len(JobCard.objects.filter(routeassigned__routedetail__billcycle=billcycle,is_deleted=False,is_active=True,reading_month = currentmonth))
                                totalMeterReadingCompleted = MeterReading.objects.filter(jobcard__routeassigned__routedetail__billcycle=billScheduledetail.billSchedule.bill_cycle.id, reading_status='complete', reading_month = currentmonth,is_deleted=False)
                                totalreading=len(totalMeterReadingCompleted)
                                if totalreading==total:
                                  completed=completed+1
                                  readindingcompletedstatus=True
                                  isdispatched=False
                                else:
                                    readindingcompletedstatus=False
                                    incomplete=incomplete+1
                                    pass

                            else:
                             pending=pending+1
                         except:
                              pass

                         try:
                             revisitcase=False
                             revisit=MeterReading.objects.filter(jobcard__routeassigned__routedetail__billcycle=billScheduledetail.billSchedule.bill_cycle.id,reading_status='revisit', reading_month = currentmonth,is_deleted=False)
                             if revisit:
                                revisitcase=True
                         except:
                          pass

                         objlist = {
                            'bill_cycle_name':billScheduledetail.billSchedule.bill_cycle.bill_cycle_name,
                            'billcycle':billScheduledetail.billSchedule.bill_cycle,
                            'startdate': billScheduledetail.start_date.strftime('%d/%m/%Y'),
                            'enddate': billScheduledetail.end_date.strftime('%d/%m/%Y'),
                            'totalroutes': len(totalroute),
                            'totalconsumer': len(totalconsumer),
                            'readindingcompletedstatus':readindingcompletedstatus,
                            'isdispatched':isdispatched,
                            'revisitcase':revisitcase,
                            'currentmonth':reading_month,
                            'month':monthh,
                            'is_schedule_completed':is_schedule_completed,
                            'Notstrted':Notstrted,
                            'notstared':notstared,

                             }
                         finallist.append(objlist)


                except:
                  pass
        except:
          pass

    data={'finallist':finallist}
    return render(request,'dispatch/jobcardfilter.html',data)

@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_dispatch(request, billcycle_id, month = None):
    routeArray=[]
    objectList={}
    finalList=[]
    data={}
    reading_completed=0
    pending=0
    prev_record = None
    next_record = None
    currentmonth = None
    completed=0

    filter_date = datetime.date.today() 
    if month:
        currentmonth = month
    else:
        currentmonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month )


    try:
        billschedulemonth=BillScheduleDetails.objects.get(billSchedule__bill_cycle=billcycle_id,month=currentmonth,last_confirmed=True)
        monthh=monthhh(billschedulemonth.month)
        billschedules = BillSchedule.objects.get(bill_cycle=billcycle_id, month = currentmonth,is_deleted=False)
        try:
            is_schedule_completed=False
            if billschedules.is_uploaded:
                is_schedule_completed=True
            else:
                pass
            billScheduledetail=BillScheduleDetails.objects.get(billSchedule=billschedules, month = currentmonth,last_confirmed=True,end_date__lt=filter_date)
            is_schedule_completed=True
        except:
          pass
        
    except:
        pass

    try:
        monthYears = []
        for month in range(0, SHOW_MONTH):
            date = datetime.date.today() - dateutil.relativedelta.relativedelta(months=month)
            monthYears.append({'value': str(date.year) + checkMonth(date.month),
                               'text': Months[date.month] + ' ' + str(date.year)})

        yearMonth=str(datetime.date.today().year) + checkMonth(datetime.date.today().month)
    except:
        pass

    try:
        billcycle = BillCycle.objects.get(id=billcycle_id)
        try:
            next_issue = BillCycle.objects.filter(id__gt=billcycle_id)[:1]
            try:
                billSchedule = BillSchedule.objects.get(bill_cycle_id=next_issue[0].id, month = currentmonth)
                next_record = next_issue[0].id
            except BillSchedule.DoesNotExists:
                pass
        except:
            pass

        try:
            prev_issue = BillCycle.objects.filter(id__lt=billcycle_id)[:1]

            try:
                billSchedule = BillSchedule.objects.get(bill_cycle_id=prev_issue[0].id, month = currentmonth)
                prev_record = prev_issue[0].id

            except BillSchedule.DoesNotExists:
                pass
        except:
            pass


        routes = RouteDetail.objects.filter(billcycle=billcycle, bill_month = currentmonth,is_deleted=False).order_by('route_code')
        total=len(routes)
        totalPending = 0
        totalDispatched = 0
        started = 0
        completed = 0

        for route in routes:
            status = "Not Dispatched"
            is_active = False
            sent_to_mr = False
            is_reading_completed=False
            reading_completed=0
            currentmr=None
            totalConsumer = ConsumerDetails.objects.filter(route=route, bill_month = currentmonth,is_deleted=False)
            totalconsumer=len(totalConsumer)

            try:
                routeassignmentobj=RouteAssignment.objects.get(routedetail=route,is_deleted = False,reading_month=currentmonth)
                jobcardcount=len(JobCard.objects.filter(~Q(meterreader=None),routeassigned=routeassignmentobj,is_active=True,is_deleted=False,is_reading_completed=True,reading_month=currentmonth))
                reading_completed=jobcardcount
                if jobcardcount==totalconsumer:
                  routeassignmentobj.is_reading_completed=True
                  routeassignmentobj.save()
                  is_reading_completed=True
                else:
                  routeassignmentobj.is_reading_completed=False
                  routeassignmentobj.save()
                  is_reading_completed=False
            except :
              pass

            try:
                currentmr='NA'
                routeassignment=RouteAssignment.objects.get(routedetail=route,is_deleted = False,reading_month = currentmonth)
                try:
                    currentmr=routeassignment.meterreader.first_name
                except:
                  pass

                if routeassignment.dispatch_status == 'Started':
                    started = started + 1
                elif routeassignment.dispatch_status == 'Dispatched' and routeassignment.is_reading_completed==True:
                    completed = completed + 1
                elif routeassignment.dispatch_status == 'Dispatched' and routeassignment.is_reading_completed==False:
                    totalDispatched=totalDispatched+1
                elif routeassignment.dispatch_status == 'Partial':
                    totalPending=totalPending+1
                else:
                  pass
                status = routeassignment.dispatch_status
                is_active = routeassignment.is_active

            except Exception,e:
                totalPending=totalPending+1
                pass

            try:
                Inprocess=False
                routeProcess=RouteProcess.objects.get(routedetail__id=route.id,reading_month=currentmonth,is_processing=True)
                if routeProcess:
                    status="Inprocess"
                    Inprocess=True

            except Exception, e:
              pass
            objectList={
                'billcycle':billcycle,
                'totalConsumer':len(totalConsumer),
                'route':route,
                'status':status,
                'is_active':is_active,
                # 'sent_to_mr':sent_to_mr,
                'reading_completed': reading_completed,
                'currentmr':currentmr,
                'is_reading_completed':is_reading_completed,
                'Inprocess':Inprocess,
                'is_schedule_completed':is_schedule_completed,


            }
            finalList.append(objectList)

    except Exception as e:
        pass

    data = {'finalLlist': finalList,'total':total,'totalDispatched':totalDispatched,'pending':totalPending, 'prev_record':prev_record, 'next_record':next_record,'started':started,'currentmonth':currentmonth,'bill_cycle_code':billcycle.bill_cycle_code,'start_date':billschedulemonth.start_date,'month':monthh,'completed':completed}
    return render(request,'dispatch/dispatch_details.html',data)

@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_mrlist(request):
    route_id = request.POST.get('route_id')
    current_month = request.POST.get('current_month')
    routeassignedcount=0
    routeassignedcountsuggest=0
    suggested=[]
    meterReaders=[]
    lastmrroutecount=0
    lastmr=[]
    count=0
    monthh=monthhh(current_month)
    route = RouteDetail.objects.get(id=route_id, bill_month = current_month)
    billschedule=BillSchedule.objects.filter(bill_cycle=route.billcycle, month = current_month)
    billScheduledetail=BillScheduleDetails.objects.get(billSchedule=billschedule, month = current_month,last_confirmed=True)
    meterReadersobj=UserProfile.objects.filter(type='METER_READER',status='ACTIVE',is_deleted=False)

    try:
        for meterreader in meterReadersobj:
            avaliability=Availability.objects.get(validator=meterreader,available='AVAILABLE')
            routeassignedcount=len(RouteAssignment.objects.filter(meterreader=meterreader,reading_month=current_month,is_reading_completed=False,is_active=True,is_deleted=False))
            if routeassignedcount < 4 and avaliability:
               count=count+1
               meterreaderobj={
                  'id':meterreader.id,
                  'employee_id':meterreader.employee_id,
                  'first_name':meterreader.first_name,
                  'contact_no':meterreader.contact_no,
                  'username':meterreader.username,
                  'routeassignedcountsuggest':len(RouteAssignment.objects.filter(meterreader=meterreader,reading_month=current_month,is_reading_completed=False,is_active=True,is_deleted=False)),
                  'count':count,
               }

               meterReaders.append(meterreaderobj)
    except:
        pass

    suggestedobj=PreferredRoutes.objects.filter(route = route.route_code,is_deleted='NO')
    try:
        suggestobj={}
        for suggest in suggestedobj:
            routeassignedcountsuggest=len(RouteAssignment.objects.filter(meterreader=suggest.user,reading_month=current_month,is_reading_completed=False,is_active=True,is_deleted=False))
            avaliability=Availability.objects.get(validator=suggest.user,available='AVAILABLE')
            if routeassignedcountsuggest < 4 and avaliability:
               suggestobj={
                    'id': suggest.user.id,
                    'employee_id':suggest.user.employee_id,
                    'first_name':suggest.user.first_name,
                    'contact_no':suggest.user.contact_no,
                    'username':suggest.user.username,
                    'routeassignedcountsuggest':len(RouteAssignment.objects.filter(meterreader=suggest.user,reading_month=current_month,is_reading_completed=False,is_active=True,is_deleted=False)),
                }
            suggested.append(suggestobj)

    except Exception, e:
        pass

    try:
        lastmrfound=False
        lastmeterreader =None
        lastmrroutecount=0

        meterReadersobj=UserProfile.objects.filter(type='METER_READER',)
        lastmr= RouteAssignment.objects.get(routedetail=route,is_deleted = False,reading_month=route.month)
        lastmrroutecount=len(RouteAssignment.objects.filter(meterreader=lastmr.meterreader,reading_month=current_month,is_reading_completed=False,is_active=True,is_deleted=False))
        avaliability=Availability.objects.get(validator=lastmr.meterreader,available='AVAILABLE')

        if lastmrroutecount < 4 and avaliability:
            lastmeterreader={
              'id': lastmr.meterreader.id,
              'employee_id':lastmr.meterreader.employee_id,
              'first_name':lastmr.meterreader.first_name,
              'contact_no':lastmr.meterreader.contact_no,
              'username':lastmr.meterreader.username,
              'lastmrroutecount':lastmrroutecount,
              }
            lastmeterreader.append(lastmeterreader)

    except Exception, e:
        pass

    currentmrNames = None

    try:
        currentmr=False
        currentmrNames=RouteAssignment.objects.get(routedetail=route,reading_month=current_month,is_deleted=False,is_active=True)
        if currentmrNames:
                currentmr=True

    except Exception, e:
        pass

    data = {'meterReaders':meterReaders,'suggested':suggested,'lastmr':lastmeterreader,'billcyclecode':route.billcycle.bill_cycle_code,'routecode':route.route_code,'routeid':route.id,'billScheduledetail':billScheduledetail,'current_month':current_month,'currentmr':currentmr,'currentmrNames':currentmrNames,'monthh':monthh}
    data = render(request,"dispatch/mr_blank.html", data)
    return HttpResponse(data)

@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def search_mr(request):

    searchTxt = request.POST.get('searchTxtDispatchModal')
    current_month = request.POST.get('current_month')

    meterReaders = []
    meterReadersobj = None
    count=0

    if searchTxt == "":
        meterReadersobj = UserProfile.objects.filter(type='METER_READER',status='ACTIVE',is_deleted=False)
    else:
        meterReadersobj = UserProfile.objects.filter( (Q(employee_id__icontains= searchTxt) | Q(username__icontains =searchTxt )),type='METER_READER',status='ACTIVE',is_deleted=False)

    try:
        for meterreader in meterReadersobj:
            routeassignedcount=len(RouteAssignment.objects.filter(meterreader=meterreader,is_active=True,is_deleted=False,reading_month=current_month,is_reading_completed=False))
            available=Availability.objects.filter(validator=meterreader,available='AVAILABLE')
            if routeassignedcount < 4 and available:
               count=count+1
               meterreaderobj={
                  'id':meterreader.id,
                  'employee_id':meterreader.employee_id,
                  'first_name':meterreader.first_name,
                  'contact_no':meterreader.contact_no,
                  'username':meterreader.username,
                  'routeassignedcountsuggest':routeassignedcount,
                  'count':count
               }
               meterReaders.append(meterreaderobj)

    except Exception, e:
      pass

    data = {'meterReaders':meterReaders}
    data = render(request,"dispatch/searchmr_blank.html", data)
    return HttpResponse(data)

# ________________________________________________________________________________________________________________________________________
# Task file call

@csrf_exempt
@login_required(login_url='/')
def assign_samemr(request):
    route=request.GET.get('route_id')

    try:
        lastmr= RouteAssignment.objects.get(routedetail=route, is_deleted = False,reading_month=route.month,is_active=True)
        lastmrid=lastmr.meterreader
        lastmrroutecount=len(RouteAssignment.objects.filter(meterreader=lastmrid,reading_month=route.bill_month))
        availables=Availability.objects.get(validator=lastmrid,available='AVAILABLE')

        if lastmrroutecount < 4 and availables:
            aysnc_assign_mr.delay(lastmrid,request.POST.get('route_id'),request.POST.get('current_month'))

    except:
        pass
    return HttpResponse(data)

@csrf_exempt
@login_required(login_url='/')
def assign_samemr_revisit(request):
    route=request.GET.get('route_id')

    try:
        lastmr=RouteAssignment.objects.get(routedetail=route, is_deleted = False,reading_month=route.bill_month,is_active=True)
        availables=Availability.objects.get(validator=lastmr.meterreader,available='AVAILABLE')

        if availables:
           aysnc_assign_revisit_mr.delay(lastmrid,request.POST.get('route_id'),request.POST.get('current_month'))

    except:
      pass
    return HttpResponse(data)


@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def assign_mr(request):

    routeid=request.POST.get('routeid')
    current_month=request.POST.get('current_month')

    try:
        routeProcess=RouteProcess.objects.get(routedetail__id=routeid,reading_month=current_month)

        if routeProcess:
            routeProcess.is_processing=True
            routeProcess.save()

    except RouteProcess.DoesNotExist:
          routeProcess = RouteProcess(
          routedetail_id= routeid,
          reading_month=current_month,
          is_processing=True,
          )
          routeProcess.save()

    aysnc_assign_mr.delay(request.POST.get('ss'), request.POST.get('routeid'), request.POST.get('current_month'))
    data = {'success':'success'}
    return HttpResponse(data)

@csrf_exempt
@login_required(login_url='/')
def assign_mr_revisit (request):
    routeid=request.POST.get('routeid')
    current_month=request.POST.get('current_month')

    try:
        routeProcess=RouteProcess.objects.get(routedetail__id=routeid,reading_month=current_month)
        if routeProcess:
            routeProcess.is_processing=True
            routeProcess.save()

    except RouteProcess.DoesNotExist:
          routeProcess = RouteProcess(
          routedetail_id= routeid,
          reading_month=current_month,
          is_processing=True,
          )
          routeProcess.save()

    aysnc_assign_mr_revisit.delay(request.POST.get('ss'), request.POST.get('routeid'), request.POST.get('current_month'))
    data = {'success':'success'}
    return HttpResponse(data)




@csrf_exempt
@login_required(login_url='/')
def deassign_mr(request):

    routeid=request.POST.get('route_id')
    current_month=request.POST.get('current_month')

    try:
        routeProcess=RouteProcess.objects.get(routedetail__id=routeid,reading_month=current_month)

        if routeProcess:
            routeProcess.is_processing=True
            routeProcess.save()

    except RouteProcess.DoesNotExist:
          routeProcess = RouteProcess(
          routedetail_id= routeid,
          reading_month=current_month,
          is_processing=True,
          )
          routeProcess.save()

    aysnc_deassign_mr.delay(request.POST.get('route_id'),request.POST.get('current_month'))
    data = {'success':'success'}
    return HttpResponse(data)


@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def assign_mr_revisit_list(request):

  routeid=request.POST.get('routeid')
  current_month=request.POST.get('current_month')
  jobcard_id=request.POST.get('jobcard_id')

  aysnc_assign_mr_revisit_list.delay(request.POST.get('ss'), request.POST.get('routeid'), request.POST.get('current_month'),request.POST.get('jobcard_id'))
  data = {'success':'success'}
  return HttpResponse(data)

@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def deassign_mr_revisit(request):

    routeid=request.POST.get('route')
    current_month=request.POST.get('bill_month')
    jobcard_id=request.POST.get('jobcard_id')

    aysnc_deassign_mr_revisit.delay(request.POST.get('route'),request.POST.get('bill_month'),request.POST.get('jobcard_id'))
    data = {'success':'success'}
    return HttpResponse(data)


# task file call end here
# _________________________________________________________________________________________________________________________________________________________________________________________
@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_revisit(request,billcycle_id,month):
    objlist={}
    finallist=[]
    data=[]
    totalRoutesRevisitCase = []
    last_mr="NA"
    totalroute=0
    
    count=0
    notdispatched=0
    completed=0
    is_schedule_completed=False

    filter_date = datetime.date.today()
    is_schedule_completed=False
    billschedules = BillSchedule.objects.get(bill_cycle=billcycle_id, month = month,is_deleted=False)
    if billschedules.is_uploaded:
        is_schedule_completed=True
    else:
      pass
    bill_schedule=BillScheduleDetails.objects.get(billSchedule=billschedules, month = month,last_confirmed=True)
    monthh=monthhh(bill_schedule.month)
    try:
        billScheduledetail=BillScheduleDetails.objects.get(billSchedule=billschedules, month = month,last_confirmed=True,end_date__lt=filter_date)
        is_schedule_completed=True
    except :
      pass
    billcyclecode=billschedules.bill_cycle.bill_cycle_code
    try:
        routes=RouteDetail.objects.filter(billcycle=billcycle_id, bill_month = month)
        for route in routes:
            jobcardsentcount=0
            try:
                routeassignment=RouteAssignment.objects.get(routedetail=route,is_deleted=False,reading_month=month)
                jobcards=JobCard.objects.filter(is_revisit=True,routeassigned=routeassignment,is_active=True,is_deleted=False,reading_month=month)
                if jobcards:
                  totalRoutesRevisitCase.append(route)
                  totalroute=totalroute+1

                for jobcard in jobcards:
                    last_mr="NA"
                    currentmr=False
                    if jobcard.meterreader:
                        last_mr=jobcard.meterreader.first_name
                        currentmr=True
                        jobcard_id=jobcard.id

                        if jobcard.is_reading_completed:
                            completed=completed+1
                        else:
                            count=count+1

                    else:
                      notdispatched=notdispatched+1

                    jobcard_id=jobcard.id
                    route_id=route

                    objlist={
                      'route':route,
                      'name':jobcard.consumerdetail.name,
                      'consumer_no':jobcard.consumerdetail.consumer_no,
                      'contact_no':jobcard.consumerdetail.contact_no,
                      'email_id':jobcard.consumerdetail.email_id,
                      'meter_no':jobcard.consumerdetail.meter_no,
                      'last_mr':last_mr,
                      'currentmr':currentmr,
                      'status':jobcard.record_status,
                      'jobcard_id':jobcard_id,
                      'is_readingcompleted':jobcard.is_reading_completed,
                      'is_schedule_completed':is_schedule_completed,

                      }
                    finallist.append(objlist)
            except  RouteAssignment.DoesNotExist:
                pass
    except:
        pass
    data = {'consumerDetails':finallist,'totalRoutesRevisitCase':totalRoutesRevisitCase,'bill_month':month,'billcycle':billcycle_id,'totalroute':totalroute,'count':count,'notdispatched':notdispatched,'completed':completed,'billcyclecode':billcyclecode,'month':monthh}
    return render(request,'dispatch/revisit.html',data)

@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def filter_revisit(request):
  route = request.POST.get('rout_code')
  month = request.POST.get('month')
  billcycle=request.POST.get('billcycle')

  totalConsumers=0
  data=[]
  objlist={}
  finallist=[]

  billScheduledetail=BillScheduleDetails.objects.get(billSchedule__bill_cycle=billcycle,month=month,last_confirmed=True)
  filter_date=datetime.date.today()

  print 'Request in with---', request.POST

  is_schedule_completed=False
  billschedules = BillSchedule.objects.get(bill_cycle=billcycle, month = month,is_deleted=False)
  if billschedules.is_uploaded:
        is_schedule_completed=True
  else:
    pass
  try:
      billScheduledetail=BillScheduleDetails.objects.get(billSchedule=billschedules, month = month,last_confirmed=True,end_date__lt=filter_date)
      is_schedule_completed=True
  except :
    pass

  try:
      if route != 'All':
        jobcards=JobCard.objects.filter(is_revisit=True,routeassigned__routedetail=route,is_active=True,is_deleted=False,reading_month=month)
        routecode=RouteDetail.objects.get(id=route,billcycle=billcycle, bill_month = month)

        for jobcard in jobcards:

            currentmr=False
            last_mr='NA'

            if jobcard.meterreader is None:
                pass
            else:
                last_mr=jobcard.meterreader.first_name
                currentmr=True

            totalConsumers=totalConsumers+1
            objlist={
                    'route_code':routecode.route_code,
                    'route':route,
                    'name':jobcard.consumerdetail.name,
                    'consumer_no':jobcard.consumerdetail.consumer_no,
                    'contact_no':jobcard.consumerdetail.contact_no,
                    'email_id':jobcard.consumerdetail.email_id,
                    'meter_no':jobcard.consumerdetail.meter_no,
                    'last_mr':last_mr,
                    'currentmr':currentmr,
                    'billcycle':jobcard.routeassigned.routedetail.billcycle,
                    'status':jobcard.record_status,
                    'is_readingcompleted':jobcard.is_reading_completed,
                    'jobcard_id':jobcard.id,
                    'is_schedule_completed':is_schedule_completed,
                                 }
            finallist.append(objlist)

      else:

        totalRoutesRevisitCase=[]
        totalConsumers=0
        routes=RouteDetail.objects.filter(billcycle=billcycle, bill_month = month)

        for route in routes:
          try:
              routecode=RouteDetail.objects.get(id=route.id,billcycle=billcycle, bill_month = month)
              jobcardsentcount=0
              routeassignment=RouteAssignment.objects.get(routedetail=routecode,is_deleted=False,reading_month=month)
              jobcards=JobCard.objects.filter(is_revisit=True,routeassigned=routeassignment,is_active=True,is_deleted=False,reading_month=month)
              if jobcards:
                  for jobcard in jobcards:
                      currentmr=False
                      last_mr='NA'

                      if jobcard.meterreader is not None:
                          last_mr=jobcard.meterreader.first_name
                          lastmrid=jobcard.routeassigned.meterreader.id
                          currentmr=True

                      jobcard_id=jobcard.id
                      route_id=route

                      objlist={
                        'route_code':routecode.route_code,
                        'route':route,
                        'name':jobcard.consumerdetail.name,
                        'consumer_no':jobcard.consumerdetail.consumer_no,
                        'contact_no':jobcard.consumerdetail.contact_no,
                        'email_id':jobcard.consumerdetail.email_id,
                        'meter_no':jobcard.consumerdetail.meter_no,
                        'last_mr':last_mr,
                        'currentmr':currentmr,
                        'billcycle':jobcard.routeassigned.routedetail.billcycle,
                        'status':jobcard.record_status,
                        'is_readingcompleted':jobcard.is_reading_completed,
                        'jobcard_id':jobcard_id,
                        'is_schedule_completed':is_schedule_completed,

                        }
                      finallist.append(objlist)
          except Exception,e:
              print e
              pass
  except Exception,e :
    print e
    pass

  data = {'consumerDetails':finallist,'bill_month':month,'billcycle':billcycle}
  data = render(request,"dispatch/revisit_consumer_list.html", data)
  return HttpResponse(data)

@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_revisit_jobcard(request,billcycle_id,month):
    objlist={}
    finallist=[]
    data=[]
    
    
    is_schedule_completed=False
    jobcardcount=0
    routecount=0
    totalrevisit=0

    bill_schedule=BillScheduleDetails.objects.get(billSchedule__bill_cycle=billcycle_id,month=month,last_confirmed=True)
    filter_date = datetime.date.today()
    is_schedule_completed=False
    billschedules = BillSchedule.objects.get(bill_cycle=billcycle_id, month = month,is_deleted=False)
    if billschedules.is_uploaded:
      is_schedule_completed=True
    else:
      pass
    try:
        billScheduledetail=BillScheduleDetails.objects.get(billSchedule=billschedules, month = month,last_confirmed=True,end_date__lt=filter_date)
        is_schedule_completed=True
    except:
      pass

    monthh=monthhh(bill_schedule.month)
    routes=RouteDetail.objects.filter(billcycle=billcycle_id, bill_month = month,is_deleted=False)
    for route in routes:
        status = "pending"
        cureentmr="N.A"
        jobcardsentcount=0
        totalConsumer=0
        try:
            Inprocess=False
            routeProcess=RouteProcess.objects.get(routedetail__id=route.id,reading_month=month,is_processing=True)
            if routeProcess:
                status="Inprocess"
                Inprocess=True
        except:
            pass
        try:
            routeassignments=RouteAssignment.objects.get(routedetail=route,reading_month=month,is_deleted=False)
            try:
                cureentmr = routeassignments.meterreader.first_name
            except:
              pass

            jobcards=JobCard.objects.filter(meterreader=None,routeassigned__routedetail=route,is_revisit=True,reading_month=month,is_reading_completed=False,is_active=True)
            jobcardcount=len(jobcards)
            totalrevisit=totalrevisit+jobcardcount

            if jobcards:
              routecount=routecount+1
              objlist={

                'route':route,
                'jobcardcount':jobcardcount,
                'startdate': bill_schedule.start_date,
                'enddate': bill_schedule.end_date,
                'cureentmr':cureentmr,
                'status':status,
                'is_schedule_completed':is_schedule_completed,
              }
              finallist.append(objlist)
        except:
          pass

    data = {'consumerDetails':finallist,'month':monthh,'billcycle':bill_schedule.billSchedule.bill_cycle,'totalrevisit':totalrevisit,'bill_month':bill_schedule.month,'routecount':routecount}
    return render(request,'dispatch/revisit_jobcard_view.html',data)


@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_mrlist_revisit(request):
    route_id = request.POST.get('route_id')
    current_month = request.POST.get('current_month')
    routeassignedcount=0
    routeassignedcountsuggest=0
    suggested=[]
    meterReaders=[]
    count=0

    route = RouteDetail.objects.get(id=route_id, bill_month = current_month)
    billschedule=BillSchedule.objects.filter(bill_cycle=route.billcycle, month = current_month)
    billScheduledetail=BillScheduleDetails.objects.get(billSchedule=billschedule, month = current_month,last_confirmed=True)

    meterReadersobj=UserProfile.objects.filter(type='METER_READER')
    try:
        for meterreader in meterReadersobj:
            avaliability=Availability.objects.get(validator=meterreader,available='AVAILABLE')
            routeassignedcount=len(RouteAssignment.objects.filter(meterreader=meterreader,is_reading_completed=False))
            if routeassignedcount < 4 and avaliability:
               count=count+1
               meterreaderobj={
                  'id':meterreader.id,
                  'employee_id':meterreader.employee_id,
                  'first_name':meterreader.first_name,
                  'contact_no':meterreader.contact_no,
                  'username':meterreader.username,
                  'routeassignedcountsuggest':len(RouteAssignment.objects.filter(meterreader=meterreader,is_reading_completed=False)),
                  'count':count
               }

               meterReaders.append(meterreaderobj)
    except:
        pass

    suggestedobj=PreferredRoutes.objects.filter(route = route.route_code,is_deleted='NO')
    try:
        suggestobj={}
        for suggest in suggestedobj:
            routeassignedcountsuggest=len(RouteAssignment.objects.filter(meterreader=suggest.user,is_reading_completed=False,reading_month=current_month,is_active=True,is_deleted=False))
            avaliability=Availability.objects.get(validator=suggest.user,available='AVAILABLE')
            if routeassignedcountsuggest < 4 and avaliability:
               suggestobj={
                    'id': suggest.user.id,
                    'employee_id':suggest.user.employee_id,
                    'first_name':suggest.user.first_name,
                    'contact_no':suggest.user.contact_no,
                    'username':suggest.user.username,
                    'routeassignedcountsuggest':len(RouteAssignment.objects.filter(meterreader=suggest.user,is_reading_completed=False,reading_month=current_month,is_active=True,is_deleted=False)),
                }
            suggested.append(suggestobj)
    except Exception, e:
        pass

    currentmrNames = None
    try:
        currentmr=False
        currentmrcount=0
        currentmrNames=RouteAssignment.objects.get(~Q(meterreader=None),routedetail=route,reading_month=current_month,is_deleted=False)
        currentmrcount=len(RouteAssignment.objects.filter(meterreader=currentmrNames.meterreader,reading_month=current_month,is_deleted=False,is_reading_completed=False,is_active=True))
        if currentmrNames:
                currentmr=True
    except Exception, e:
        pass

    data = {'meterReaders':meterReaders,'suggested':suggested,'billcyclecode':route.billcycle.bill_cycle_code,'routecode':route.route_code,'routeid':route.id,'billScheduledetail':billScheduledetail,'current_month':current_month,'currentmr':currentmr,'currentmrNames':currentmrNames,'currentmrcount':currentmrcount}
    data = render(request,"dispatch/mrlist_revisit.html", data)
    return HttpResponse(data)



@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def search_mr_revisit(request):
    meterReaders = []
    searchTxt = request.POST.get('searchTxtDispatchModal')
    current_month = request.POST.get('current_month')
    meterReadersobj = None

    if searchTxt == "":
        meterReadersobj = UserProfile.objects.filter(type='METER_READER',is_deleted=False,status='ACTIVE')
    else:
        meterReadersobj = UserProfile.objects.filter( (Q(employee_id__icontains= searchTxt) | Q(username__icontains =searchTxt )),type='METER_READER',is_deleted=False,status='ACTIVE')

    count=0
    try:
        for meterreader in meterReadersobj:
            routeassignedcount=len(RouteAssignment.objects.filter(meterreader=meterreader,is_deleted=False,is_active=True,reading_month=current_month,is_reading_completed=False))
            available=Availability.objects.get(validator=meterreader,available='AVAILABLE')
            if routeassignedcount < 4 and available:
               count=count+1
               meterreaderobj={
                  'id':meterreader.id,
                  'employee_id':meterreader.employee_id,
                  'first_name':meterreader.first_name,
                  'contact_no':meterreader.contact_no,
                  'username':meterreader.username,
                  'routeassignedcountsuggest':routeassignedcount,
                  'count':count
               }
               meterReaders.append(meterreaderobj)

    except Exception, e:
      pass

    data = {'meterReaders':meterReaders}
    data = render(request,"dispatch/searchmr_revisit.html", data)
    return HttpResponse(data)




@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_mrlist_revisit_list(request):

    route_id = request.POST.get('route')
    current_month = request.POST.get('bill_month')
    jobcard_id = request.POST.get('jobcard_id')

    routeassignedcount=0
    routeassignedcountsuggest=0
    suggested=[]
    meterReaders=[]
    next_record = None
    count=0

    route = RouteDetail.objects.get(id=route_id, bill_month = current_month)
    billschedule=BillSchedule.objects.filter(bill_cycle=route.billcycle, month = current_month)
    billScheduledetail=BillScheduleDetails.objects.get(billSchedule=billschedule, month = current_month,last_confirmed=True)

    meterReadersobj=UserProfile.objects.filter(type='METER_READER')
    try:
        for meterreader in meterReadersobj:
            avaliability=Availability.objects.get(validator=meterreader,available='AVAILABLE')
            routeassignedcount=len(RouteAssignment.objects.filter(meterreader=meterreader,is_reading_completed=False))
            if routeassignedcount < 4 and avaliability:
               count=count+1
               meterreaderobj={
                  'id':meterreader.id,
                  'employee_id':meterreader.employee_id,
                  'first_name':meterreader.first_name,
                  'contact_no':meterreader.contact_no,
                  'username':meterreader.username,
                  'routeassignedcountsuggest':len(RouteAssignment.objects.filter(meterreader=meterreader,is_reading_completed=False)),
                  'count':count
               }

               meterReaders.append(meterreaderobj)
    except:
        pass

    suggestedobj=PreferredRoutes.objects.filter(route = route.route_code,is_deleted='NO')
    try:
        suggestobj={}
        for suggest in suggestedobj:
            routeassignedcountsuggest=len(RouteAssignment.objects.filter(meterreader=suggest.user,is_reading_completed=False,reading_month=current_month,is_active=True,is_deleted=False))
            avaliability=Availability.objects.get(validator=suggest.user,available='AVAILABLE')
            if routeassignedcountsuggest < 4 and avaliability:
               suggestobj={
                    'id': suggest.user.id,
                    'employee_id':suggest.user.employee_id,
                    'first_name':suggest.user.first_name,
                    'contact_no':suggest.user.contact_no,
                    'username':suggest.user.username,
                    'routeassignedcountsuggest':len(RouteAssignment.objects.filter(meterreader=suggest.user,is_reading_completed=False,reading_month=current_month,is_active=True,is_deleted=False)),
                }
            suggested.append(suggestobj)
    except Exception, e:
        pass

    currentmrNames = None
    try:
        currentmr=False
        currentmrcount=0
        currentmrNames=RouteAssignment.objects.get(~Q(meterreader=None),routedetail=route.id,reading_month=current_month,is_deleted=False)
        currentmrcount=len(RouteAssignment.objects.filter(meterreader=currentmrNames.meterreader,reading_month=current_month,is_deleted=False,is_reading_completed=False,is_active=True))
        if currentmrNames:
                currentmr=True
    except Exception, e:
        pass

    data = {'meterReaders':meterReaders,'suggested':suggested,'billcyclecode':route.billcycle.bill_cycle_code,'routecode':route.route_code,'routeid':route.id,'billScheduledetail':billScheduledetail,'current_month':current_month,'currentmr':currentmr,'currentmrNames':currentmrNames,'currentmrcount':currentmrcount,'jobcard':jobcard_id}
    data = render(request,"dispatch/revisit_mr_listlevel.html", data)
    return HttpResponse(data)


def revisit_list_exporttoexcel(request,billcycle_id,bill_month):
  try:
      month=bill_month
      billcycle = BillCycle.objects.get(id = billcycle_id)
      response = HttpResponse(content_type='text/csv')
      response['Content-Disposition'] = 'attachment; filename="revisitlist' + str(
          billcycle.bill_cycle_code) + '_' + str(month) +  '.csv"';
      writer = csv.writer(response, delimiter=' ', quotechar='"', quoting=csv.QUOTE_ALL)
      writer.writerow(['RouteID', 'Consumer Number', 'Consumer Name', 'Meter Number', 'Meter Reader Name','Status'])

      billcycle = None
      route_id = None
      allData = []
      routes=RouteDetail.objects.filter(billcycle=billcycle_id, bill_month = month)
      for route in routes:
          jobcardsentcount=0
          try:
              routeassignment=RouteAssignment.objects.get(routedetail=route,is_deleted=False,reading_month=month)
              jobcards=JobCard.objects.filter(is_revisit=True,routeassigned=routeassignment,is_active=True,is_deleted=False,reading_month=month)
              if jobcards:

                for jobcard in jobcards:
                    jobcard_id=jobcard.id
                    route_id=route
                    route_code=route.route_code
                    bill_cycle_code=route.billcycle.bill_cycle_code

                    tempList = []
                    tempList.append(str(route_code))
                    tempList.append(str("'")+str(jobcard.consumerdetail.consumer_no).encode('utf-8'))
                    tempList.append(jobcard.consumerdetail.name)
                    tempList.append(str(jobcard.consumerdetail.meter_no))

                    tempList.append(( jobcard.meterreader.first_name + ' ' + jobcard.meterreader.last_name).encode('utf-8'))
                    tempList.append(jobcard.record_status)
                    writer.writerow(tempList)

          except  RouteAssignment.DoesNotExist:
              pass

          return response
  except Exception, e:
    print e
  data = {'success': 'false'}
  return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def refresh(request):
  current_month = request.POST.get('current_month')
  jobcardcount=0
  count=0
  try:

      routeassignmentobjs=RouteAssignment.objects.filter(is_deleted = False,reading_month=current_month)
      for routeassignmentobj in routeassignmentobjs:
        try:
          count=count +1
          jobcards=JobCard.objects.filter(~Q(meterreader=None),routeassigned=routeassignmentobj,is_active=True,is_deleted=False,is_reading_completed=True,reading_month=current_month)
          if jobcards:
            jobcardcount=len(jobcards)
            totalConsumer = ConsumerDetails.objects.filter(route=routeassignmentobj.routedetail, bill_month = current_month,is_deleted=False)
            totalconsumer=len(totalConsumer)
            reading_completed=jobcardcount
            if jobcardcount==totalconsumer:
              routeassignmentobj.is_reading_completed=True
              routeassignmentobj.save()
            else:
              routeassignmentobj.is_reading_completed=False
              routeassignmentobj.save()
        except:
          pass

      data = {'success':'success'}
  except:
    pass

    data = {'success':'success'}
  return HttpResponse(json.dumps(data), content_type='application/json')



def meaterreadinddata(request):
    return render(request,'dispatch/revisit.html')


# functions for dummy data dump into the database
def savedata(request):

    today = datetime.date.today()
    employetype = EmployeeType(
        employee_type='permanant',
        created_by='admin',
        updated_by='admin',
        created_date=today,
        updated_date=today,
        is_deleted='False'
    )
    employetype.save()
    today = datetime.date.today()
    for privilege in privileges:
        userPrivilege = UserPrivilege(
            privilege=privilege,
            created_by='admin',
            updated_by='admin',
            created_date=datetime.date.today(),
            updated_date=datetime.date.today(),
            is_deleted='False'
        )
        userPrivilege.save()
    print 'All privileges created\n'


    userrole = UserRole(
                    role='MeterReader',
                    description='metereader',
                    status='ACTIVE',
                    created_by='admin',
                    updated_by='admin',
                    created_date=today,
                    updated_date=today,
                    is_deleted='False'
            )


    userrole.save()

    state = State.objects.get(state='Maharashtra')
    city = City.objects.get(city='Pune')
    for i in range (1,10):
        userprofile = UserProfile(
            username='mrvijay' +str(i) + '@bynry.com',
            first_name='mrvijay'+ str(i),
            email='meterreadervijay'+str(i) + '@bynry.com',
            date_joined=today,
            contact_no='8007271914',
            last_name='reader'+str(i),
            address_line_1='abc',
            address_line_2='Pune',
            city=city,
            state=state,
            pincode="123123",
            role=userrole,
            employee_id='123' +str(i),
            employee_type=employetype,
            type='METER_READER',
            status='Active',
            updated_by='admin',
            created_date=today,
            updated_date=today,
            is_deleted='False'
        )
        userprofile.save()

        devicedetail = DeviceDetail(
        company_name='Essel',
        device_name='Samsung',
        make='Essel',
        imei_no='12340' + str(i),
        user_id=userprofile,
        is_deleted='No',
        device_details_created_by='admin',
        device_details_updated_by='admin',
        device_details_created_date=today,
        device_details_updated_date=today
        )

        devicedetail.save()

def savedata_billcycle(request):

    today = datetime.date.today()
    utility = Utility(
        utility='Electricity',
        created_by='admin',
        updated_by='admin',
        created_date=today,
        updated_date=today,

    )
    utility.save()
    for i in range(1, 2):
        state = State(
            state='Maharashtra',
            created_by='admin',
            updated_by='admin',
            created_date=today,
            updated_date=today,

        )
        state.save()
        for j in range(1, 2):
            city = City(
                city='Pune',
                state=state,
                created_by='admin',
                updated_by='admin',
                created_date=today,
                updated_date=today,

            )
            city.save()
            for k in range(200, 205):
                billcycle = BillCycle(
                    bill_cycle_code=k,
                    city=city,
                    utility=utility,
                    bill_cycle_name='Shubham' + str(k),
                    created_by='admin',
                    updated_by='admin',
                    created_date=today,
                    updated_date=today,
                )
                billcycle.save()

                for l in range(1000, 1005):
                    routedetail = RouteDetail(
                        route_code=l,
                        billcycle=billcycle,
                        month = '201608',
                        bill_month='201609',
                        created_by='admin',
                        updated_by='admin',
                        created_on=today,
                        updated_on=today
                    )
                    routedetail.save()

                    for c in range(1, 6):
                        consumer = ConsumerDetails(
                            month='201608',
                            bill_month = '201609',
                            name='shubham' + str(c),
                            # consumer_last_name='pawar',
                            email_id='shubham.pawar' + str(c) + '@bynry.com',
                            contact_no='8007271913',
                            address_line_1="ABC Road",
                            address_line_2='Mumbai',
                            city=city,
                            pin_code='222343',
                            route=routedetail,
                            bill_cycle=billcycle,
                            meter_no='688686',
                            dtc='123',
                            pole_no='88888',
                            created_by='admin',
                            updated_by='admin',
                            created_date=today,
                            updated_date=today,
                        )
                        consumer.save()
