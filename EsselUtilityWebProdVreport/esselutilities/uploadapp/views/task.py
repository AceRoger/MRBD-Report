import json
import pdb
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
import datetime
from django.conf import settings
from consumerapp.models import ConsumerDetails
from dispatch.models import MeterReading, JobCard, MeterStatus, ReaderStatus
from scheduleapp.models import BillSchedule, PN33Download, UploadB30
from adminapp.models import City, BillCycle, RT_MASTER, RT_DETAILS, RouteDetail, UPLD_MTR_RDNG
from suds.client import Client
from celery import task
from django.utils import timezone
from django.db import transaction
import time
import operator
import itertools
import traceback

import shutil

__author__ = 'vkmchandel'


@task
def store_reading_staging_tbl(uploadB30):

    try:
        uploadObj = uploadB30
        billCycleObj = uploadObj.bill_schedule.bill_cycle
        consumerDetails = ConsumerDetails.objects.filter(bill_cycle=billCycleObj, bill_month=uploadObj.month)
        print 'consumerDetails', consumerDetails
        i = 1

        consumer_list_rt = []
        consumer_list_rnt = []
        for consumerDetail in consumerDetails:
            try:
                uploadedTime = timezone.now()

                try:
                    meterReading = MeterReading.objects.get(jobcard__consumerdetail=consumerDetail,
                                                            reading_status='complete', is_active=True)
                except MeterReading.MultipleObjectsReturned:
                    meterReading = MeterReading.objects.filter(jobcard__consumerdetail=consumerDetail,
                                                               reading_status='complete', is_active=True).first()

                print 'consumerDetail', consumerDetail
                print 'meterReading', meterReading
                print '======================'

                record = {'ID': consumerDetail.id, 'BILL_CYC': consumerDetail.bill_cycle.bill_cycle_code,
                          'BILL_MONTH': consumerDetail.bill_month,
                          'CUSTOMER_ID': consumerDetail.consumer_no,
                          'DOCUMENT_TYPE': 'B30', 'DTR_NO': consumerDetail.dtc, 'ESTIMATED': '0',
                          'FEEDER_CODE': consumerDetail.feeder_code,
                          'IMAGE_PATH': '', 'INSERTEDON': uploadedTime, 'LATTITUDE': meterReading.latitude,
                          'LONGITUDE': meterReading.longitude,
                          'MDI': '', 'METER_READING': meterReading.current_meter_reading_v2,
                          'METER_STATUS': meterReading.meter_status_v2.status_code,
                          'PC': consumerDetail.feeder_code, 'PF': '',
                          'READER_ID': meterReading.jobcard.meterreader.employee_id,
                          # 'READING_DATE': meterReading.reading_date.strftime("%d%m%y"),
                          'READING_DATE': meterReading.reading_date,
                          'ROUTE': consumerDetail.route.route_code, 'SEQUENCE': 'SEQUENCE'
                          }
                i = i + 1
                consumer_list_rt.append(record)
            except MeterReading.DoesNotExist, e:
                record = {'ID': consumerDetail.id, 'BILL_CYC': consumerDetail.bill_cycle.bill_cycle_code,
                          'BILL_MONTH': consumerDetail.bill_month,
                          'CUSTOMER_ID': consumerDetail.consumer_no,
                          'DOCUMENT_TYPE': 'B30', 'DTR_NO': consumerDetail.dtc, 'ESTIMATED': '0',
                          'FEEDER_CODE': consumerDetail.feeder_code,
                          'IMAGE_PATH': '', 'INSERTEDON': uploadedTime, 'LATTITUDE': '',
                          'LONGITUDE': '',
                          'MDI': '', 'METER_READING': '',
                          'METER_STATUS': '7',
                          'PC': consumerDetail.feeder_code, 'PF': '',
                          'READER_ID': '',
                          'READING_DATE': '',
                          'ROUTE': consumerDetail.route.route_code, 'SEQUENCE': 'SEQUENCE'
                          }
                i = i + 1
                consumer_list_rnt.append(record)

        consumer_list_rt.sort(key=operator.itemgetter('READER_ID'))

        consumer_group_list = []
        for key, items in itertools.groupby(consumer_list_rt, operator.itemgetter('READER_ID')):
            consumer_group_list.append(list(items))

        consumer_final_list = []
        srNo = 0;

        for consumers in consumer_group_list:
            consumers.sort(key=operator.itemgetter('READING_DATE'))
            for consumer in consumers:
                srNo = srNo + 1;
                SQ = str(consumer['BILL_MONTH']) + str(consumer['READER_ID']) + str(check_srno(srNo))

                b30_obj = UPLD_MTR_RDNG(
                    BILL_CYC=consumer['BILL_CYC'],
                    BILL_MONTH=consumer['BILL_MONTH'],
                    CUSTOMER_ID=consumer['CUSTOMER_ID'],
                    DOCUMENT_TYPE=consumer['DOCUMENT_TYPE'],
                    DTR_NO=checkInteger(consumer['DTR_NO']),
                    ESTIMATED=consumer['ESTIMATED'],
                    FEEDER_CODE=consumer['FEEDER_CODE'],
                    IMAGE_PATH=consumer['IMAGE_PATH'],
                    INSERTEDON=consumer['INSERTEDON'],
                    LATTITUDE=consumer['LATTITUDE'],
                    LONGITUDE=consumer['LONGITUDE'],
                    MDI=consumer['MDI'],
                    METER_READING=consumer['METER_READING'],
                    METER_STATUS=consumer['METER_STATUS'],
                    PC=consumer['PC'],
                    PF=consumer['PF'],
                    READER_ID=consumer['READER_ID'],
                    READING_DATE=consumer['READING_DATE'],
                    ROUTE=consumer['ROUTE'],
                    SEQUENCE=SQ,
                )
                b30_obj.save()

        for consumer in consumer_list_rnt:
            srNo = srNo + 1;
            SQ = str(consumer['BILL_MONTH']) + str(consumer['READER_ID']) + str(check_srno(srNo))
            b30_obj = UPLD_MTR_RDNG(
                BILL_CYC=consumer['BILL_CYC'],
                BILL_MONTH=consumer['BILL_MONTH'],
                CUSTOMER_ID=consumer['CUSTOMER_ID'],
                DOCUMENT_TYPE=consumer['DOCUMENT_TYPE'],
                DTR_NO=checkInteger(consumer['DTR_NO']),
                ESTIMATED=consumer['ESTIMATED'],
                FEEDER_CODE=consumer['FEEDER_CODE'],
                IMAGE_PATH=consumer['IMAGE_PATH'],
                INSERTEDON=consumer['INSERTEDON'],
                LATTITUDE=consumer['LATTITUDE'],
                LONGITUDE=consumer['LONGITUDE'],
                MDI=consumer['MDI'],
                METER_READING=consumer['METER_READING'],
                METER_STATUS=consumer['METER_STATUS'],
                PC=consumer['PC'],
                PF=consumer['PF'],
                READER_ID=consumer['READER_ID'],
                READING_DATE=consumer['READING_DATE'],
                ROUTE=consumer['ROUTE'],
                SEQUENCE=SQ,
            )
            b30_obj.save()

        bill_cycle_code=uploadB30.bill_schedule.bill_cycle.bill_cycle_code
        month=uploadB30.month
        b30_count = UPLD_MTR_RDNG.objects.filter(BILL_MONTH=month,BILL_CYC=bill_cycle_code).count()
        total_consumer = consumerDetails.filter().count()

        print 'b30_count==>',b30_count
        print 'total_consumer==>',total_consumer

        if b30_count == total_consumer:
            complete_uploadB30(uploadB30)
            upload_b30(uploadB30)
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|task.py|save_b30_table', e
        fail_uploadB30(uploadB30)


def checkInteger(number):
    try:
        return int(number)
    except:
        return None

def upload_b30(uploadB30):
    try:
        print 'upload30================>'
        city=uploadB30.bill_schedule.bill_cycle.city.city
        utility=uploadB30.bill_schedule.bill_cycle.utility.utility
        bill_cycle_code=uploadB30.bill_schedule.bill_cycle.bill_cycle_code
        month=uploadB30.month

        soapClient_uploadb30 = Client(settings.UPLOADB30_URL)
        routeDetails = RouteDetail.objects.filter(billcycle=uploadB30.bill_schedule.bill_cycle, bill_month=month)

        print 'routeDetails',routeDetails
        print 'soapClient_uploadb30',soapClient_uploadb30

        for routeDetail in routeDetails:
            soapResponse = soapClient_uploadb30.service.execute(city,utility,bill_cycle_code, month,
                                                                routeDetail.route_code)
        time.sleep(60)
        complete_uploadB30(uploadB30)
    except Exception,e:
        print 'Exception|task.py|upload_b30', e
        fail_uploadB30(uploadB30)


def fail_uploadB30(uploadB30):
    try:
        bill_cycle_code=uploadB30.bill_schedule.bill_cycle.bill_cycle_code
        month=uploadB30.month
        UPLD_MTR_RDNG.objects.filter(BILL_CYC=bill_cycle_code,BILL_MONTH=month).delete()
        uploadB30.status = 'Failed'
        uploadB30.save()
        return True
    except Exception, e:
        print 'Exception|task.py|fail_uploadB30', e
    return False


def complete_uploadB30(uploadB30):
    try:
        print 'complete_uploadB30==============>', uploadB30
        uploadB30.status = 'Completed'
        uploadB30.end_date = timezone.now()
        uploadB30.save()

        billSchedule=uploadB30.bill_schedule
        billSchedule.is_uploaded=True
        billSchedule.save()
        return True
    except Exception, e:
        print 'Exception|task.py|complete_downloadPN33', e
    return False



def check_srno(srNo):
    if srNo < 10:
        return '000' + str(srNo)
    elif srNo >= 10 and srNo < 100:
        return '00' + str(srNo)
    elif srNo >= 100 and srNo < 1000:
        return '0' + str(srNo)
    else:
        return srNo



# def store_reading_not_taken(consumer_list_rnt,uploadB30):
#     try:
#         jobcard_list=[]
#         reading_list=[]
#         for record in consumer_list_rnt:
#             print 'record',record
#             consumerDetail = ConsumerDetails.objects.get(id=record['ID'])
#             try:
#                 jobcard = JobCard.objects.get(consumerdetail=consumerDetail, is_active=True)
#             except JobCard.MultipleObjectsReturned:
#                 jobcard = JobCard.objects.filter(consumerdetail=consumerDetail, is_active=True).first()
#             except JobCard.DoesNotExist:
#                 jobcard = JobCard(
#                     routeassigned=None,
#                     consumerdetail=consumerDetail,
#                     meterreader=None,
#                     #completion_date=billscheduledetail.end_date,
#                     reading_month=record['BILL_MONTH'],
#                     is_active=True,
#                     record_status='COMPLETED',
#                     is_reading_completed=True,
#                     created_by='admin',
#                 )
#                 jobcard.save()
#                 jobcard_list.append(jobcard.id)
#
#             meterReading = MeterReading(
#                 jobcard=jobcard,
#                 current_meter_reading=record['METER_READING'],
#                 image_url='',
#                 meter_status=MeterStatus.objects.get(meter_status='ReadingNotTaken'),
#                 reader_status=ReaderStatus.objects.get(reader_status='Normal'),
#                 reading_status='',
#                 is_assigned_to_v1=False,
#                 is_assigned_to_v2=False,
#                 longitude='',
#                 latitude='',
#                 reading_month=record['BILL_MONTH'],
#                 reading_date=None,
#                 #suspicious_activity=reading_date,
#                 meter_status_v1=MeterStatus.objects.get(meter_status='ReadingNotTaken'),
#                 reader_status_v1=ReaderStatus.objects.get(reader_status='Normal'),
#                 comment_v1='',
#                 current_meter_reading_v1=record['METER_READING'],
#                 meter_status_v2=MeterStatus.objects.get(meter_status='ReadingNotTaken'),
#                 reader_status_v2=ReaderStatus.objects.get(reader_status='Normal'),
#                 comment_v2='',
#                 current_meter_reading_v2=record['METER_READING'],
#             )
#             meterReading.save()
#             reading_list.append(meterReading.id)
#         return True
#     except Exception, e:
#         print 'Exception|task.py|store_reading_not_taken', e
#         JobCard.objects.filter(id__in=jobcard_list).delete()
#         MeterReading.objects.filter(id__in=reading_list).delete()
#         fail_uploadB30(uploadB30)
#         return False