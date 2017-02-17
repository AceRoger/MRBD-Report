from decimal import Decimal
import traceback
from xlrd import open_workbook, xldate_as_tuple

import json
import pdb
from django.http import HttpResponse
from django.shortcuts import render
import datetime

from consumerapp.models import ConsumerDetails
from dispatch.models import RouteAssignment, JobCard, MeterReading, MeterStatus, ReaderStatus
from scheduleapp.models import BillSchedule, PN33Download, UploadB30, BillScheduleDetails
from adminapp.models import City, BillCycle, RT_MASTER, RT_DETAILS, RouteDetail, UserProfile
from suds.client import Client
from celery import task
from django.utils import timezone
from django.db import transaction

from adminapp import constraints
import traceback

__author__ = 'vkm chandel'


@transaction.atomic
def read_exl(request):
    try:



        # file_path = ['/home/bynry-01/MRBD/history-data/data/116_PN33_JUN.XLSX',
        #             '/home/bynry-01/MRBD/history-data/data/PN33_116_JULY.xlsx',
        #             '/home/bynry-01/MRBD/history-data/data/116_PN33_MAY.XLSX']

        # file_path = ['/home/bynry-01/Desktop/data-history/PN33/history_data_new/107_APR.xls',
        #             '/home/bynry-01/Desktop/data-history/PN33/history_data_new/107_FEB.xls',
        #             '/home/bynry-01/Desktop/data-history/PN33/history_data_new/107_MAR.xls',
        #             '/home/bynry-01/Desktop/data-history/PN33/history_data_new/116-APR.xls',
        #             '/home/bynry-01/Desktop/data-history/PN33/history_data_new/116_FEB.xls',
        #             '/home/bynry-01/Desktop/data-history/PN33/history_data_new/116-MAR.xls',
        #             '/home/bynry-01/Desktop/data-history/PN33/history_data_new/117-APR.xls',
        #             '/home/bynry-01/Desktop/data-history/PN33/history_data_new/117-FEB.xls',
        #             '/home/bynry-01/Desktop/data-history/PN33/history_data_new/117-MAR.xls']


        # file_path = ['/root/HistoryData/history_data-ii/107_APR.xls',
        #             '/root/HistoryData/history_data-ii/107_FEB.xls',
        #             '/root/HistoryData/history_data-ii/107_MAR.xls',
        #             '/root/HistoryData/history_data-ii/116-APR.xls',
        #             '/root/HistoryData/history_data-ii/116_FEB.xls',
        #             '/root/HistoryData/history_data-ii/116-MAR.xls',
        #             '/root/HistoryData/history_data-ii/117-APR.xls',
        #             '/root/HistoryData/history_data-ii/117-FEB.xls',
        #             '/root/HistoryData/history_data-ii/117-MAR.xls']
        #
        # file_path=['/home/bynry-01/Desktop/data-history/PN33/test-data/143-Aug.xls']

        file_path=['/root/DATA3/MAY-135.xlsx','/root/DATA3/JUN-135.xlsx','/root/DATA4/135_SEP.xlsx']
        #file_path=['/root/DATA3/APR-135.xlsx','/root/DATA3/AUG-135.xlsx','/root/DATA3/JUL-135.xlsx','/root/DATA3/JUN-135.xlsx','/root/DATA3/MAR-135.xlsx','/root/DATA3/MAY-135.xlsx']


        for file in file_path:
            print file
            wb = open_workbook(file)
            values = []
            print 'wb.sheets()', wb.sheets()
            number_of_rows = wb.sheets()[0].nrows
            number_of_columns = wb.sheets()[0].ncols
            print 'number_of_rows', number_of_rows
            print 'number_of_columns', number_of_columns

            for row in range(1, number_of_rows):
                row_values = []
                for col in range(number_of_columns):
                    value = (wb.sheets()[0].cell(row, col).value)
                    try:
                        value = str(int(value))
                    except ValueError:
                        pass
                    finally:
                        row_values.append(value)
                values.append(row_values)
            #print 'values', values
            sid = transaction.savepoint()
            store_consumer(values, sid)
            transaction.savepoint_commit(sid)

        # store_consumer('101')
    except Exception, e:
        #print 'exception ',str(traceback.print_exc())
        print 'Exception', e
        transaction.rollback(sid)


def store_consumer(valueLists, sid):
    try:
        # pdb.set_trace()
        bill_cycle = ''
        month = ''

        route_code=""
        i=0
        for valueList in valueLists:

            if valueList[2]=="" or valueList[2].strip()=="" or valueList[2].strip()=='NA':
                continue

            #print 'valueList[2]',valueList[2]
            prev_billCycle=None
            try:
                billCycleObj = BillCycle.objects.get(bill_cycle_code=valueList[2].strip())
                prev_billCycle=billCycleObj
            except BillCycle.DoesNotExist:
                billCycleObj=prev_billCycle

            routeObj = check_route_obj(valueList[31], get_ym(valueList[15]), billCycleObj)

            print 'routeObj===>',routeObj
            if routeObj is None:
                print '======================================='
                print 'valueList[31]',valueList[31]
                print 'valueList[31]',get_ym(valueList[15])
                print 'valueList[2]',valueList[2]
                print '======================================='
                raise Exception('error while route load')

            bill_cycle = valueList[2]
            month = get_ym(valueList[15])
            consumerDetails = ConsumerDetails(
                name=valueList[8],
                consumer_no=check_consumer(valueList[5]),
                #consumer_no=valueList[5],
                email_id='',
                contact_no='',
                address_line_1=valueList[10],
                address_line_2=valueList[11],
                address_line_3=valueList[12],
                city=City.objects.get(city='Muzaffarpur'),
                pin_code='',
                route=routeObj,
                bill_cycle=billCycleObj,
                feeder_code=valueList[25],
                feeder_name=valueList[26],
                meter_no=valueList[36],
                dtc=valueList[27],
                dtc_dec=valueList[28],
                pole_no=valueList[34],
                meter_digit=valueList[41],
                connection_status=valueList[20],
                month=constraints.month_minus(get_ym(valueList[15])),
                bill_month=get_ym(valueList[15]),
                lattitude=valueList[52],
                longitude=valueList[53],
                prev_feeder_code=valueList[4],
                prev_reading=valueList[46],

                #curr_reading_date=None,
                curr_reading_date=store_date(valueList[45]),
                prev_reading_date=store_date(valueList[44]),
                killowatt=valueList[21],
                consumption=valueList[47],
                avg_six_months=valueList[50]).save()

            i=i+1

        save_schedule(bill_cycle, month, sid)
    except Exception, e:
        #print 'exception ',str(traceback.print_exc())
        print 'index==>',i
        print '------------------------------------'
        print 'bill_cycle',bill_cycle
        print 'exception ', str(traceback.print_exc())
        print 'DataLoad error ===> ', e
        transaction.rollback(sid)


def check_consumer(consumer_no):
    if len(consumer_no)<12:
        zero=12-len(consumer_no)
        return '0'*zero+str(consumer_no)
    else:
        return consumer_no


def get_ym(bill_month):
    if bill_month == '' or bill_month == None or bill_month == 'NA':
        return None
    else:
        if len(bill_month)==8:
            return bill_month[:-2]
        elif len(bill_month)==6:
            return bill_month



def save_schedule(billCycle, month, sid):
    try:
        billCycleObj = BillCycle.objects.get(bill_cycle_code=billCycle)

        print '-------------schedule save-----------------'
        print billCycle
        print month
        print '-------------schedule save-----------------'


        billSchedule = BillSchedule(
            bill_cycle=billCycleObj,
            month=month,
            created_by='Admin'
        )
        billSchedule.save()
        print 'month',month
        startDate = '01/' + month[-2:] + '/' + month[:-2]
        endDate = '10/' + month[-2:] + '/' + month[:-2]
        accounting_d = '01/' + month[-2:] + '/' + month[:-2]
        estimated_d = '10/' + month[-2:] + '/' + month[:-2]
        billScheduleDetails = BillScheduleDetails(
            billSchedule=billSchedule,
            month=billSchedule.month,
            start_date=datetime.datetime.strptime(startDate, '%d/%m/%Y'),
            end_date=datetime.datetime.strptime(endDate, '%d/%m/%Y'),
            accounting_date=datetime.datetime.strptime(accounting_d, '%d/%m/%Y'),
            estimated_date=datetime.datetime.strptime(estimated_d, '%d/%m/%Y'),
            last_confirmed='True',
            status='Confirmed',
            is_original='True',
            is_active='True',
            created_by='Admin'
        )
        billScheduleDetails.save()
        startd = datetime.datetime.strptime('Jun 1 2016  1:00PM', '%b %d %Y %I:%M%p')
        endd = datetime.datetime.strptime('Jun 1 2016  4:00PM', '%b %d %Y %I:%M%p')

        pn33Download = PN33Download(
            month=billSchedule.month,
            bill_schedule=billSchedule,
            start_date=startd,
            end_date=endd,
            asy_job_id='xyz',
            download_status='Completed',
            created_by='Admin'
        )
        pn33Download.save()
        uploadB30 = UploadB30(
            month=billSchedule.month,
            bill_schedule=billSchedule,
            status='Not Started',
            created_by='Admin'
        )
        uploadB30.save()


        mr=UserProfile.objects.get(email='vkm@gmail.com')
        for route in RouteDetail.objects.filter(billcycle=billCycleObj):
            dispatch(mr,route,uploadB30.month,sid)

    except Exception, e:
        #print 'exception ',str(traceback.print_exc())
        print 'Exception|schedule.py|save_schedule', e
        transaction.rollback(sid)


def dispatch(mr_id, route_id, current_month,sid):
    try:
        today = datetime.date.today()
        #print route_id
        route = route_id
        billschedule = BillSchedule.objects.get(bill_cycle=route.billcycle, month=current_month)
        billscheduledetail = BillScheduleDetails.objects.get(billSchedule=billschedule, month=current_month)
        routeassignment = None

        routeassignment = RouteAssignment(
            routedetail=route,
            meterreader=mr_id,
            assign_date=today,
            due_date=billscheduledetail.end_date,
            reading_month=current_month,
            dispatch_status='Dispatched',
            is_reading_completed=True,
            is_active=True,
            sent_to_mr=True,
            created_by='admin',
        )

        routeassignment.save()

        consumerdetails = ConsumerDetails.objects.filter(route=route, bill_month=current_month)
        reading_date = datetime.datetime.strptime('Jun 1 2016  1:00PM', '%b %d %Y %I:%M%p')


        for consumerdetail in consumerdetails:
            jobcard = JobCard(
                routeassigned=routeassignment,
                consumerdetail=consumerdetail,
                meterreader=mr_id,
                completion_date=billscheduledetail.end_date,
                reading_month=current_month,
                is_active=True,
                record_status='COMPLETED',
                is_reading_completed=True,
                created_by='admin',
            )
            jobcard.save()


            if consumerdetail.consumption=='' or consumerdetail.consumption==None or consumerdetail.consumption=='NA':
                meterReading = MeterReading(
                    jobcard=jobcard,
                    current_meter_reading=consumerdetail.consumption,
                    image_url='',
                    meter_status=MeterStatus.objects.get(meter_status='ReadingNotTaken'),
                    reader_status=ReaderStatus.objects.get(reader_status='Normal'),
                    reading_status='complete',
                    is_assigned_to_v1=True,
                    is_assigned_to_v2=True,
                    longitude='',
                    latitude='',
                    reading_month=billscheduledetail.month,
                    reading_date=reading_date,
                    #reading_date=consumerdetail.curr_reading_date,
                    #suspicious_activity=reading_date,
                    meter_status_v1=MeterStatus.objects.get(meter_status='ReadingNotTaken'),
                    reader_status_v1=ReaderStatus.objects.get(reader_status='Normal'),
                    comment_v1='',
                    current_meter_reading_v1=consumerdetail.consumption,
                    meter_status_v2=MeterStatus.objects.get(meter_status='ReadingNotTaken'),
                    reader_status_v2=ReaderStatus.objects.get(reader_status='Normal'),
                    comment_v2='',
                    current_meter_reading_v2=consumerdetail.consumption,
                ).save()
            else:
                meterReading = MeterReading(
                    jobcard=jobcard,
                    current_meter_reading=consumerdetail.consumption,
                    image_url='/sitemedia/images/'+billschedule.bill_cycle.bill_cycle_code+'/'+billschedule.month+'/'+consumerdetail.consumer_no+'.JPG',
                    meter_status=MeterStatus.objects.get(meter_status='Normal'),
                    reader_status=ReaderStatus.objects.get(reader_status='Normal'),
                    reading_status='complete',
                    is_assigned_to_v1=True,
                    is_assigned_to_v2=True,
                    longitude='',
                    latitude='',
                    reading_month=billscheduledetail.month,
                    reading_date=reading_date,
                    #suspicious_activity=reading_date,
                    meter_status_v1=MeterStatus.objects.get(meter_status='Normal'),
                    reader_status_v1=ReaderStatus.objects.get(reader_status='Normal'),
                    comment_v1='',
                    current_meter_reading_v1=consumerdetail.consumption,
                    meter_status_v2=MeterStatus.objects.get(meter_status='Normal'),
                    reader_status_v2=ReaderStatus.objects.get(reader_status='Normal'),
                    comment_v2='',
                    current_meter_reading_v2=consumerdetail.consumption,
                ).save()

    except Exception, e:
        #print 'exception ',str(traceback.print_exc())
        print 'Exception',e
        transaction.rollback(sid)
        print "An unexpected error occured !!"



def check_route_obj(route, month, billCycleObj):
    try:
        routeDetail = RouteDetail.objects.get(route_code=route, bill_month=month,billcycle=billCycleObj)
        return routeDetail
    except RouteDetail.DoesNotExist, e:
        routeDetail = RouteDetail(
            route_code=route,
            billcycle=billCycleObj,
            month=constraints.month_minus(month),
            bill_month=month,
        )
        routeDetail.save()
        return routeDetail
    except Exception, e:
        print 'Exception', e
        return None


def checkMonth(month):
    if month > 9:
        return str(month)
    else:
        return '0' + str(month)


def store_date(date):
    if date == '' or date == None or date == 'NA':
        return None
    else:
        # print '==========dfdsfds===========================',date
        # print xldate_as_tuple(int(date),0)
        # print '====================================='
        year, month, day, hour, minute, second=xldate_as_tuple(int(date),0)
        date=str(checkMonth(day))+'/'+str(checkMonth(month))+'/'+str(year)
        date=date.strip()
        #print date
        #print datetime.datetime.strptime(date, '%d/%m/%Y')
        return datetime.datetime.strptime(date, '%d/%m/%Y')


def store_decimal(date):
    if date == '' or date == None:
        return None
    else:
        return Decimal(date)


@transaction.atomic
def check_reading(request):
     try:
         sid=transaction.savepoint()
         meterReading=MeterReading.objects.filter(reading_month__in=["201607","201606","201605","201604","201603","201602"])
         i=1

         for reading in meterReading:
             if reading.current_meter_reading:
                 if not reading.image_url:
                     print 'index',i
                     print 'reading.current_meter_reading',reading.current_meter_reading
                     print 'reading.image_url',reading.image_url

                     month=reading.reading_month
                     bill_cycle=reading.jobcard.consumerdetail.bill_cycle
                     consumer_no=reading.jobcard.consumerdetail.consumer_no
                     reading.image_url='/sitemedia/images/'+bill_cycle.bill_cycle_code+'/'+month+'/'+consumer_no+'.JPG'
                     reading.save()
                     print 'reading.current_meter_reading',reading.current_meter_reading
                     i=i+1

         print len(meterReading)
     except Exception,e:
         transaction.rollback(sid)
         print 'Exception',e

from django.db.models.functions import Length

@transaction.atomic
def consumer_id_12digit(request):
     try:
         sid=transaction.savepoint()
         #meterReading=MeterReading.objects.annotate(consumer_ln=Length('jobcard__consumerdetail__consumer_no')).filter(reading_month__in=["201607","201606","201605","201604","201603","201602"],consumer_ln__lt=12)
         meterReading=MeterReading.objects.annotate(consumer_ln=Length('jobcard__consumerdetail__consumer_no')).filter(reading_month__in=["201608"],consumer_ln__lt=12)
         #meterReading=MeterReading.objects.filter(reading_month__in=["201607","201606","201605","201604","201603","201602"],jobcard__consumerdetail__contact_no)

         print 'meterReading',meterReading

         i=1
         for reading in meterReading:
             consumer=reading.jobcard.consumerdetail
             temp_consumer_no=check_consumer(consumer.consumer_no)
             consumer.consumer_no=temp_consumer_no
             consumer.save()

             month=reading.reading_month
             bill_cycle=reading.jobcard.consumerdetail.bill_cycle
             consumer_no=reading.jobcard.consumerdetail.consumer_no
             reading.image_url='/sitemedia/images/'+bill_cycle.bill_cycle_code+'/'+month+'/'+consumer_no+'.JPG'
             reading.save()
             print 'reading.current_meter_reading',reading.image_url
             i=i+1
             print i

         print len(meterReading)
     except Exception,e:
         transaction.rollback(sid)
         print 'Exception',e



def store_consuemer_data(valueLists):
    try:
        for valueList in valueLists:
            rt_details = RT_DETAILS(
                CIS_DIVISION=valueList[1],
                BILL_CYC_CD=valueList[2],
                BU=valueList[3],
                PC=valueList[4],
                CONS_NO=valueList[5],
                ACCOUNT_ID=valueList[6],
                MU_NO=valueList[7],
                CONS_NAME=valueList[8],
                FATH_HUS_NAME=valueList[9],
                ADD1=valueList[10],
                ADD2=valueList[11],
                ADD3=valueList[12],
                VILLAGE=valueList[13],
                PREV_MONTH=valueList[14],
                BILL_MONTH=valueList[15],
                CURR_MONTH=valueList[16],
                BILL_NO=valueList[17],
                TRF_CATG=valueList[18],
                CONN_DATE=valueList[19],
                CONS_STATUS=valueList[20],
                LOAD=valueList[21],
                LOAD_UNIT_CD=valueList[22],
                DUTY_CD=valueList[23],
                URBAN_FLG=valueList[24],
                FEEDER_CD=valueList[25],
                FEEDER_NAME=valueList[26],
                DTC_CD=valueList[27],
                DTC_DESC=valueList[28],
                AREA_CD=valueList[29],
                AREA_NAME=valueList[30],
                ROUTE=valueList[31],
                SEQUENCE=valueList[32],
                GR_NO=valueList[33],
                RD_NO=valueList[34],
                POLE_NO=valueList[35],
                METER_NO=valueList[36],
                MTR_INST_DT=store_date(valueList[37]),
                MTR_REPL_DT=store_date(valueList[38]),
                METER_PHASE=valueList[39],
                MAKE=valueList[40],
                METER_DIGIT=valueList[41],
                MTR_TYPE=valueList[42],
                MF=valueList[43],
                PREVIOUS_RTG_DT=store_date(valueList[44]),
                CURRENT_RTG_DT=store_date(valueList[45]),
                PREV_RTG=store_decimal(valueList[46]),
                CURR_RTG=store_decimal(valueList[47]),
                CURR_RTG_STTS=valueList[48],
                PREV_RTG_STTS=valueList[49],
                AVG=valueList[50],
                LCR_UNIT=valueList[51],
                LATTITUDE=valueList[52],
                LONITUDE=valueList[53]
            ).save()
    except Exception, e:
        print 'DataLoad error', e
