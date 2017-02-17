import csv
import json
import os
import pdb
import re
import zipfile
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
import datetime

import os.path

from adminapp import constraints
from adminapp.constraints import SHOW_MONTH
from consumerapp.models import RouteDetail, ConsumerDetails
from dispatch.models import MeterReading, JobCard, MeterStatus
from scheduleapp.models import BillSchedule, PN33Download, BillScheduleDetails, UploadB30
from adminapp.models import City, BillCycle, RT_MASTER, RT_DETAILS, UPLD_MTR_RDNG

from django.utils import timezone
from celery.result import AsyncResult
from django.db import transaction
from uploadapp.views import task
import operator
import itertools
import shutil
from django.contrib.auth.decorators import login_required
import traceback
import dateutil.relativedelta
from shutil import copyfile
from authenticateapp.decorator import role_required

from uploadapp.templatetags import uploadFilter
from django.core.exceptions import MultipleObjectsReturned

from esselutilities.settings import BASE_DIR

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
def open_upload_index(request):
    data = load_data()
    return render(request, 'uploadapp/uploadB30.html', data)


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def open_reading(request, schedule_id):
    try:
        print 'billcycle_id==>', schedule_id
        billSchedule = BillSchedule.objects.get(id=schedule_id)

        print 'billSchedule', billSchedule
        print 'billSchedule.bill_cycle.id', billSchedule.bill_cycle.id

        billCycle = BillCycle.objects.get(id=billSchedule.bill_cycle.id)

        total_record = ConsumerDetails.objects.filter(bill_cycle=billCycle, is_deleted=False,
                                                      bill_month=billSchedule.month).count()
        totalMeterReading = MeterReading.objects.filter(jobcard__consumerdetail__bill_cycle=billCycle,
                                                        reading_status='complete',
                                                        reading_month=billSchedule.month).count()
        pending = total_record - totalMeterReading

        print 'total_record', total_record
        print 'totalMeterReading', totalMeterReading
        print 'pending', pending

        meterStatus = MeterStatus.objects.all()

        data = {'routeCodes': RouteDetail.objects.filter(billcycle=billCycle,
                                                         month=constraints.month_minus(billSchedule.month)),
                'billSchedule': billSchedule,
                'total_record': total_record, 'totalMeterReading': totalMeterReading, 'pending': pending,
                'meterStatus': meterStatus}
    except Exception, e:
        print 'Exception|upload.py|open_reading', e
        data = {'error': 'server error'}
    return render(request, 'uploadapp/reading.html', data)


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_upload_summery_by_route(request):
    try:
        # pdb.set_trace()
        billSchedule_id = request.GET.get('billSchedule')
        route_code = request.GET.get('route_code')
        meterStatus = request.GET.get('meterStatus')

        billSchedule = BillSchedule.objects.get(id=billSchedule_id)
        billCycle = billSchedule.bill_cycle

        if route_code == 'All':
            total_record = ConsumerDetails.objects.filter(bill_cycle=billCycle, is_deleted=False,
                                                          bill_month=billSchedule.month).count()

            totalMeterReading = MeterReading.objects.filter(jobcard__consumerdetail__bill_cycle=billCycle,
                                                            reading_status='complete',
                                                            reading_month=billSchedule.month).count()
            pending = total_record - totalMeterReading

        else:
            routeDetail = RouteDetail.objects.get(id=route_code)

            total_record = ConsumerDetails.objects.filter(bill_cycle=billCycle, route=routeDetail, is_deleted=False,
                                                          bill_month=billSchedule.month).count()

            totalMeterReading = MeterReading.objects.filter(jobcard__consumerdetail__bill_cycle=billCycle,
                                                            jobcard__consumerdetail__route=routeDetail,
                                                            reading_status='complete',
                                                            reading_month=billSchedule.month).count()
            pending = total_record - totalMeterReading

        data = {'success': 'true',
                'total_record': total_record,
                'totalMeterReading': totalMeterReading,
                'pending': pending}

        print data
    except Exception, e:
        print 'Exception|upload.py|get_upload_summery_by_route', e
        data = {'success': 'false', 'error': 'server error'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_upload_summery(request):
    try:
        # pdb.set_trace()
        billCycle_id = request.GET.get('id')
        yearMonth = request.GET.get('yearMonth')
        billCycle = BillCycle.objects.get(id=billCycle_id)

        totalRouteDetail = RouteDetail.objects.filter(billcycle=billCycle, bill_month=yearMonth).count()
        total_record = ConsumerDetails.objects.filter(bill_cycle=billCycle, is_deleted=False,
                                                      bill_month=yearMonth).count()

        dispachedCount = JobCard.objects.filter(~Q(meterreader=None), reading_month=yearMonth,
                                                consumerdetail__bill_cycle=billCycle,
                                                is_active=True,
                                                record_status__in=['ALLOCATED', 'ASSIGNED', 'COMPLETED']).count()

        meterReading = MeterReading.objects.filter(jobcard__consumerdetail__bill_cycle=billCycle,
                                                   reading_month=yearMonth, is_active=True, is_duplicate=False,
                                                   is_deleted=False).exclude(reading_status='revisit')

        completeReading = meterReading.filter(reading_status='complete').count()
        validate1Reading = meterReading.filter(reading_status='validation1').count()
        validate2Reading = meterReading.filter(reading_status='validation2').count()

        pending = total_record - (completeReading + validate1Reading + validate2Reading)
        print '======================================='
        data = {'success': 'true', 'totalRouteDetail': totalRouteDetail, 'total_record': total_record,
                'dispachedCount': dispachedCount,
                'completeReading': completeReading,
                'validate1Reading': validate1Reading, 'validate2Reading': validate2Reading,
                'pending': pending}
        print data
    except Exception, e:
        print 'Exception|upload.py|get_upload_summery', e
        data = {'success': 'false', 'error': 'server error'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def export_b30_excel(request, upload_id):
    try:
        # yearMonth = request.GET.get('yearMonth')
        uploadObj = UploadB30.objects.get(id=upload_id)
        billCycleObj = uploadObj.bill_schedule.bill_cycle

        print 'billCycleObj', billCycleObj
        consumerDetails = ConsumerDetails.objects.filter(bill_cycle=billCycleObj, bill_month=uploadObj.month)

        print 'consumerDetails', consumerDetails

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="b30-' + str(billCycleObj.bill_cycle_code) + '.csv"';
        writer = csv.writer(response)

        i = 1
        writer.writerow(
            ['Document_Type', 'Customer_ID', 'PC', 'Meter_Status', 'Meter_Reading', 'Reading_Date', 'MDI', 'PF',
             'Bill_Month', 'Feeder_Code', 'DTR_No', 'Reader_Id', 'Sequence', 'Estimated'])

        print '==============timezone.now()',

        consumer_list_rt = []
        consumer_list_rnt = []
        for consumerDetail in consumerDetails:
            try:
                uploadedTime = timezone.now().replace(tzinfo=None).strftime("%d/%m/%Y %H:%M:%S")

                try:
                    meterReading = MeterReading.objects.get(jobcard__consumerdetail=consumerDetail,
                                                            reading_status='complete', is_active=True)
                except MeterReading.MultipleObjectsReturned:
                    meterReading = MeterReading.objects.filter(jobcard__consumerdetail=consumerDetail,
                                                               reading_status='complete', is_active=True).first()

                print 'consumerDetail', consumerDetail
                print 'meterReading', meterReading
                print '======================'

                record = {'ID': str(i), 'BILL_CYC': consumerDetail.bill_cycle.bill_cycle_code,
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
                record = {'ID': str(i), 'BILL_CYC': consumerDetail.bill_cycle.bill_cycle_code,
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
                print consumer['METER_STATUS']
                srNo = srNo + 1;
                SQ = str(consumer['BILL_MONTH']) + str(consumer['READER_ID']) + str(check_srno(srNo))
                writer.writerow(
                    [consumer['DOCUMENT_TYPE'], str(consumer['CUSTOMER_ID']), consumer['PC'],
                     consumer['METER_STATUS'],
                     consumer['METER_READING'], consumer['READING_DATE'].strftime("%d%m%y"), consumer['MDI'],
                     consumer['PF'],
                     consumer['BILL_MONTH'], consumer['FEEDER_CODE'], consumer['DTR_NO'], consumer['READER_ID'],
                     str(SQ),
                     consumer['ESTIMATED']])

        for consumer in consumer_list_rnt:
            srNo = srNo + 1;
            SQ = str(consumer['BILL_MONTH']) + str(consumer['READER_ID']) + str(check_srno(srNo))
            writer.writerow(
                [consumer['DOCUMENT_TYPE'], str(consumer['CUSTOMER_ID']), consumer['PC'],
                 consumer['METER_STATUS'],
                 consumer['METER_READING'], consumer['READING_DATE'], consumer['MDI'], consumer['PF'],
                 consumer['BILL_MONTH'], consumer['FEEDER_CODE'], consumer['DTR_NO'], consumer['READER_ID'],
                 str(SQ),
                 consumer['ESTIMATED']])

        return response
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|upload.py|export_b30_excel', e
        data = {'success': 'false', 'error': 'server error'}
    return HttpResponse(json.dumps(str(e)), content_type='application/json')


def check_srno(srNo):
    if srNo < 10:
        return '000' + str(srNo)
    elif srNo >= 10 and srNo < 100:
        return '00' + str(srNo)
    elif srNo >= 100 and srNo < 1000:
        return '0' + str(srNo)
    else:
        return srNo


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def save_b30_table(request):
    try:
        print 'Request In with',request.GET
        # pdb.set_trace()
        uploadObj = UploadB30.objects.get(id=request.GET.get('id'))

        if uploadObj.status !='Started':
            UPLD_MTR_RDNG.objects.filter(BILL_MONTH=uploadObj.month,
                                         BILL_CYC=uploadObj.bill_schedule.bill_cycle.bill_cycle_code).delete()

            taskObject = task.store_reading_staging_tbl.delay(uploadObj)
            uploadObj.start_date = timezone.now()
            uploadObj.status = 'Started'
            uploadObj.asy_job_id = taskObject.task_id
            uploadObj.updated_by =request.user.email
            uploadObj.save()

        data = {'success': 'true'}
    except Exception, e:
        print 'Exception|upload.py|save_b30_table', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_reading_list(request):
    try:
        print '=========================get_reading_list'
        # pdb.set_trace()
        consumerList = []
        print 'request.GET', request.GET

        column = request.GET.get('order[0][column]')
        searchTxt = request.GET.get('search[value]')
        order = ""
        if request.GET.get('order[0][dir]') == 'desc':
            order = "-"

        list = ['route__route_code', 'consumer_no', 'meter_no', 'name']
        column_name = order + list[int(column)]

        start = request.GET.get('start')
        length = int(request.GET.get('length')) + int(request.GET.get('start'))
        route_code = request.GET.get('route_code')
        reading_status = request.GET.get('readingStatus')
        meterStatus = request.GET.get('meterStatus')

        print 'reading_status=====>', reading_status
        print 'route_code=========>', route_code
        print 'meterStatus=========>', meterStatus

        billSchedule = BillSchedule.objects.get(id=request.GET.get('billSchedule'))
        billScheduleDetails = BillScheduleDetails.objects.get(billSchedule=billSchedule, last_confirmed=True)
        billCycle = billSchedule.bill_cycle

        consumerDetails = []

        if route_code == 'All':
            if meterStatus == 'All':
                if reading_status == 'All':
                    consumerDetails = ConsumerDetails.objects.filter(bill_cycle=billCycle, is_deleted=False,
                                                                     bill_month=billSchedule.month)

                elif reading_status == 'ReadingTaken':
                    consumerDetails = ConsumerDetails.objects.filter(is_deleted=False,
                                                                     id__in=[jobCard.consumerdetail.id for jobCard in
                                                                             JobCard.objects.filter(
                                                                                 consumerdetail__bill_cycle=billCycle,
                                                                                 is_active=True,
                                                                                 is_deleted=False,
                                                                                 reading_month=billSchedule.month,
                                                                                 record_status__in=['ALLOCATED',
                                                                                                    'ASSIGNED',
                                                                                                    'COMPLETED'])])

                elif reading_status == 'ReadingNotTaken':
                    consumerDetails = ConsumerDetails.objects.filter(bill_cycle=billCycle, is_deleted=False,
                                                                     bill_month=billSchedule.month).exclude(
                        id__in=[jobCard.consumerdetail.id for jobCard in
                                JobCard.objects.filter(is_active=True, is_deleted=False,
                                                       reading_month=billSchedule.month,
                                                       consumerdetail__bill_cycle=billCycle,
                                                       record_status__in=['ALLOCATED', 'ASSIGNED', 'COMPLETED'])])
            else:
                meterStatusObj = MeterStatus.objects.get(id=meterStatus)
                meterReadings = MeterReading.objects.filter(jobcard__consumerdetail__bill_cycle=billCycle,
                                                            reading_month=billSchedule.month,
                                                            meter_status=meterStatusObj,
                                                            is_active=True, is_duplicate=False, is_deleted=False)

                if reading_status == 'All' or reading_status == 'ReadingTaken':
                    consumerDetails = ConsumerDetails.objects.filter(
                        id__in=[meterReading.jobcard.consumerdetail.id for meterReading in meterReadings])
                else:
                    consumerDetails = ConsumerDetails.objects.none()

        else:
            routeDetail = RouteDetail.objects.get(id=route_code)
            if meterStatus == 'All':
                if reading_status == 'All':
                    consumerDetails = ConsumerDetails.objects.filter(bill_cycle=billCycle, route=routeDetail,
                                                                     is_deleted=False,
                                                                     month=constraints.month_minus(
                                                                         billSchedule.month))

                elif reading_status == 'ReadingTaken':

                    consumerDetails = ConsumerDetails.objects.filter(is_deleted=False,
                                                                     id__in=[jobCard.consumerdetail.id for jobCard in
                                                                             JobCard.objects.filter(is_active=True,
                                                                                                    is_deleted=False,
                                                                                                    consumerdetail__bill_cycle=billCycle,
                                                                                                    consumerdetail__route=routeDetail,
                                                                                                    reading_month=billSchedule.month,
                                                                                                    record_status__in=[
                                                                                                        'ALLOCATED',
                                                                                                        'ASSIGNED',
                                                                                                        'COMPLETED'])])

                elif reading_status == 'ReadingNotTaken':
                    consumerDetails = ConsumerDetails.objects.filter(bill_cycle=billCycle, route=routeDetail,
                                                                     is_deleted=False,
                                                                     bill_month=billSchedule.month).exclude(
                        id__in=[jobCard.consumerdetail.id for jobCard in
                                JobCard.objects.filter(is_active=True, is_deleted=False,
                                                       consumerdetail__bill_cycle=billCycle,
                                                       consumerdetail__route=routeDetail,
                                                       reading_month=billSchedule.month,
                                                       record_status__in=['ALLOCATED', 'ASSIGNED', 'COMPLETED'])])
            else:
                meterStatusObj = MeterStatus.objects.get(id=meterStatus)
                meterReadings = MeterReading.objects.filter(jobcard__consumerdetail__bill_cycle=billCycle,
                                                            jobcard__consumerdetail__route=routeDetail,
                                                            reading_month=billSchedule.month,
                                                            meter_status=meterStatusObj,
                                                            is_active=True, is_duplicate=False, is_deleted=False)

                print 'meterReadings======With Meter Status============>', meterReadings

                if reading_status == 'All' or reading_status == 'ReadingTaken':
                    consumerDetails = ConsumerDetails.objects.filter(
                        id__in=[meterReading.jobcard.consumerdetail.id for meterReading in meterReadings])
                else:
                    consumerDetails = ConsumerDetails.objects.none()

        total_record = consumerDetails.filter().count()
        print 'total_record', total_record
        consumerDetails = consumerDetails.filter(
            Q(consumer_no__icontains=searchTxt) | Q(meter_no__icontains=searchTxt) | Q(
                name__icontains=searchTxt)).order_by(column_name)[start:length]

        if meterStatus == 'All':
            meterReadings = MeterReading.objects.filter(jobcard__consumerdetail__bill_cycle=billCycle,
                                                        reading_month=billSchedule.month, is_active=True,
                                                        is_duplicate=False, is_deleted=False)
        else:
            meterStatusObj = MeterStatus.objects.get(id=meterStatus)
            meterReadings = MeterReading.objects.filter(jobcard__consumerdetail__bill_cycle=billCycle,
                                                        reading_month=billSchedule.month, meter_status=meterStatusObj,
                                                        is_active=True, is_duplicate=False, is_deleted=False)

        print '====================check all======================'
        # print 'meterReadings====>', meterReadings

        due_data = billScheduleDetails.end_date.strftime('%d/%m/%Y')

        print 'consumerDetails', consumerDetails

        for consumerDetail in consumerDetails:
            tempList = []

            reading_status = meterReadings.filter(jobcard__consumerdetail__id=consumerDetail.id,
                                                  jobcard__is_revisit=False, is_active=True)

            tempList.append(consumerDetail.route.route_code)
            tempList.append(consumerDetail.consumer_no)
            tempList.append(consumerDetail.meter_no)
            tempList.append(consumerDetail.name)

            if reading_status:
                if reading_status[0].current_meter_reading_v2:
                    tempList.append(reading_status[0].current_meter_reading_v2)
                elif reading_status[0].current_meter_reading_v1:
                    tempList.append(reading_status[0].current_meter_reading_v1)
                else:
                    tempList.append(reading_status[0].current_meter_reading)
            else:
                tempList.append('----')

            if reading_status:
                try:
                    tempList.append(reading_status[0].meter_status.meter_status)
                except Exception:
                    tempList.append('None')
            else:
                tempList.append('----')

            if reading_status:
                tempList.append(reading_status[0].reading_status)
            else:
                tempList.append('Not Taken')

            if reading_status:
                if reading_status[0].reading_date:
                    tempList.append(reading_status[0].reading_date.strftime("%d/%m/%Y"))
                else:
                    tempList.append('----')
            else:
                tempList.append('----')

            if reading_status:
                if reading_status[0].validated_on_v1:
                    tempList.append(reading_status[0].validated_on_v1.strftime("%d/%m/%Y"))
                else:
                    tempList.append('---')
            else:
                tempList.append('---')

            if reading_status:
                if reading_status[0].validated_on_v2:
                    tempList.append(reading_status[0].validated_on_v1.strftime("%d/%m/%Y"))
                else:
                    tempList.append('---')
            else:
                tempList.append('---')

            consumerList.append(tempList)
        data = {'iTotalRecords': total_record, 'iTotalDisplayRecords': total_record, 'aaData': consumerList}
        # print 'data', data
    except Exception, e:
        print 'Exception|upload.py|get_reading_list', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


meterStatus = {
    'DFCT':'Meter Faulty',
    'INAC':'Inaccesssible',
    'LOCK':'Locked Premise',
    'MISS':'Meter Missing',
    'NORM':'Normal',
    'NRDG':'Reading Not Taken',
    'OVR' :'Meter Overflow',
    'RPLC':'Meter Change',
}


@login_required(login_url='/')
def reading_export(request, schedule_id):
    try:

        billSchedule = BillSchedule.objects.get(id=schedule_id)

        billScheduleDetails = BillScheduleDetails.objects.get(billSchedule=billSchedule, last_confirmed=True)
        billCycle = billSchedule.bill_cycle

        consumerDetails = ConsumerDetails.objects.filter(bill_cycle=billCycle, is_deleted=False,
                                                         bill_month=billSchedule.month)

        meterReadings = MeterReading.objects.filter(jobcard__consumerdetail__bill_cycle=billCycle,
                                                    reading_month=billSchedule.month, is_active=True,
                                                    is_duplicate=False, is_deleted=False)

        due_data = billScheduleDetails.end_date.strftime('%d/%m/%Y')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="readings_for' + str(
            billCycle.bill_cycle_code) + '.csv"';
        writer = csv.writer(response)
        writer.writerow(
            ['BILL_CYC_CD', 'BILL_MONTH', 'ROUTE_CODE', 'CONSUMER_NO', 'CONSUMER_NAME', 'ADDRESS1', 'METER_NO',
             'PREV_READING', 'PREV_READING_DATE', 'PREV_RTG_STTS', 'READING STATUS',
             'CURRENT_MT_READING', 'CURRENT_MT_RDG_V1', 'CURRENT_MT_RDG_V2', 'CONSUMPTION', 'METER_STS', 'METER_STS_V1',
             'METER_STS_V2', 'READER_STS', 'READER_STS_V1', 'READER_STS_V2', 'REMARK', 'REMARK_V1', 'REMARK_V2',
             'IMG_REMARK_V1', 'IMG_REMARK_V2', 'SUSPICIOUS_ACTIVITY', 'SUSPICIOUS_ACTIVITY_REMARK', 'READING_DATE',
             'VALIDATOR1_DATE', 'VALIDATOR2_DATE', 'LATTITUDE',
             'LONGITUDE', 'METER_READER_ID', 'METER_READER_NAME', 'VALIDATOR1_NAME', 'VALIDATOR2_NAME',
             'RD_TAKEN_BY', 'REVISIT'])

        for consumerDetail in consumerDetails:
            tempList = []
            reading_status = meterReadings.filter(jobcard__consumerdetail__id=consumerDetail.id,
                                                  jobcard__is_revisit=False, is_active=True)

            tempList.append(consumerDetail.bill_cycle.bill_cycle_code)
            tempList.append(consumerDetail.bill_month)
            tempList.append(consumerDetail.route.route_code)
            # tempList.append("'" + str(consumerDetail.consumer_no))
            tempList.append("'" + str(consumerDetail.consumer_no))
            tempList.append(consumerDetail.name)
            tempList.append((consumerDetail.address_line_1).encode('utf-8'))
            tempList.append(consumerDetail.meter_no)

            pre_reading = consumerDetail.prev_reading

            tempList.append(consumerDetail.prev_reading)

            if consumerDetail.prev_reading_date:
                tempList.append(consumerDetail.prev_reading_date.strftime("%d/%m/%Y"))
            else:
                tempList.append('----')

            # tempList.append(consumerDetail.mf)

            if consumerDetail.curr_rtg_stts:
                try:
                    #meterStatus = MeterStatus.objects.get(status_code=consumerDetail.mf)
                    #tempList.append(meterStatus.meter_status)
                    tempList.append(meterStatusDist[consumerDetail.curr_rtg_stts])
                except:
                    tempList.append('----')
            else:
                tempList.append('----')

            if reading_status:
                tempList.append(reading_status[0].reading_status)
            else:
                tempList.append('Not Taken')

            if reading_status:
                tempList.append(
                    reading_status[0].current_meter_reading if reading_status[0].current_meter_reading else '----')
                tempList.append(reading_status[0].current_meter_reading_v1 if reading_status[
                    0].current_meter_reading_v1 else '----')
                tempList.append(reading_status[0].current_meter_reading_v2 if reading_status[
                    0].current_meter_reading_v2 else '----')
            else:
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')

            # ----consumption Calculation-----

            if reading_status:
                if reading_status[0].current_meter_reading_v2:
                    currentReading = reading_status[0].current_meter_reading_v2
                elif reading_status[0].current_meter_reading_v1:
                    currentReading = reading_status[0].current_meter_reading_v1
                else:
                    currentReading = reading_status[0].current_meter_reading

                # print 'currentReading==>',currentReading
                # print 'pre_reading==>',pre_reading

                try:
                    consumption = float(currentReading) - float(pre_reading)
                    tempList.append(consumption)
                except:
                    tempList.append('----')

                    # print 'consumption========',consumption

            else:
                tempList.append('----')

            if reading_status:
                try:
                    tempList.append(reading_status[0].meter_status.meter_status)
                except Exception:
                    tempList.append('----')
                try:
                    tempList.append(reading_status[0].meter_status_v1.meter_status)
                except Exception:
                    tempList.append('----')

                try:
                    tempList.append(reading_status[0].meter_status_v2.meter_status)
                except Exception:
                    tempList.append('----')
            else:
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')

            if reading_status:
                try:
                    tempList.append(reading_status[0].reader_status.reader_status)
                except Exception:
                    tempList.append('----')
                try:
                    tempList.append(reading_status[0].reader_status_v1.reader_status)
                except Exception:
                    tempList.append('----')

                try:
                    tempList.append(reading_status[0].reader_status_v2.reader_status)
                except Exception:
                    tempList.append('----')
            else:
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')

            if reading_status:
                tempList.append(reading_status[0].comment)
                tempList.append(reading_status[0].comment_v1)
                tempList.append(reading_status[0].comment_v2)
                tempList.append(reading_status[0].image_remark_v1)
                tempList.append(reading_status[0].image_remark_v2)

                if reading_status[0].suspicious_activity == True:
                    tempList.append('Yes')
                else:
                    tempList.append('No')
                tempList.append(reading_status[0].suspicious_activity_remark)
            else:
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')

            if reading_status:
                if reading_status[0].reading_date:
                    tempList.append(reading_status[0].reading_date.strftime("%d/%m/%Y %r"))
                else:
                    tempList.append('----')

                if reading_status[0].validated_on_v1:
                    tempList.append(reading_status[0].validated_on_v1.strftime("%d/%m/%Y"))
                else:
                    tempList.append('----')

                if reading_status[0].validated_on_v2:
                    tempList.append(reading_status[0].validated_on_v2.strftime("%d/%m/%Y"))
                else:
                    tempList.append('----')

                tempList.append(reading_status[0].latitude)
                tempList.append(reading_status[0].longitude)
            else:
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')

            if reading_status:
                if reading_status[0].jobcard.meterreader:
                    tempList.append(reading_status[0].jobcard.meterreader.employee_id)
                    tempList.append(reading_status[0].jobcard.meterreader.first_name + ' ' + reading_status[
                        0].jobcard.meterreader.last_name)
                else:
                    tempList.append('---')
                    tempList.append('---')

                if reading_status[0].updated_by_v1:
                    tempList.append(
                        reading_status[0].updated_by_v1.first_name + ' ' + reading_status[0].updated_by_v1.last_name)
                else:
                    tempList.append('---')

                if reading_status[0].updated_by_v2:
                    tempList.append(
                        reading_status[0].updated_by_v2.first_name + ' ' + reading_status[0].updated_by_v2.last_name)
                else:
                    tempList.append('---')
                tempList.append(reading_status[0].reading_taken_by)

                if reading_status[0].jobcard.is_revisit == True:
                    tempList.append('Yes')
                else:
                    tempList.append('No')

            else:
                tempList.append('---')
                tempList.append('---')
                tempList.append('---')
                tempList.append('---')
                tempList.append('---')
                tempList.append('---')

            writer.writerow(tempList)

        return response
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|upload.py|get_reading_list', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_bill_cycles(request):
    try:
        print '===========upload=========> get bill cycles'
        yearMonth = request.GET.get('yearMonth')
        uploadb30 = UploadB30.objects.filter(month=yearMonth, is_deleted=False).order_by(
            'bill_schedule__bill_cycle__bill_cycle_code')

        consumerDetails = ConsumerDetails.objects.filter(
            bill_cycle__in=[upload.bill_schedule.bill_cycle for upload in uploadb30], is_deleted=False,
            month=constraints.month_minus(yearMonth))
        totalConsumerDetails = consumerDetails.filter().count()

        print 'totalConsumerDetails', totalConsumerDetails
        print 'uploadb30.filter()', uploadb30.filter(status='Completed')

        uploadedConsumerCount = consumerDetails.filter(
            bill_cycle__in=[upload.bill_schedule.bill_cycle for upload in uploadb30.filter(status='Completed')],
            is_deleted=False, month=constraints.month_minus(yearMonth)).count()

        print 'totalConsumerDetails', totalConsumerDetails
        print 'uploadedConsumerCount', uploadedConsumerCount
        pending = totalConsumerDetails - uploadedConsumerCount

        totalRecords = uploadb30.filter().count()

        data = {'uploadb30': uploadb30,
                'pending': pending, 'uploaded': uploadedConsumerCount,
                'totalRecords': totalRecords,
                'Total': totalConsumerDetails}

        print 'data--', data
        data = render(request, 'uploadapp/billCyclesTailes.html', data)
    except Exception, e:
        print 'Exception|pn33.py|get_bill_cycles', e
        data = {'success': 'false', 'message': 'Server Error'}
    return HttpResponse(data)


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_bill_cycles_byfilter(request):
    try:
        print '====================> get_bill_cycles_byfilter'
        yearMonth = request.GET.get('yearMonth')
        day = request.GET.get('filterBy')
        if day != 'All':
            filter_date = datetime.date.today() + datetime.timedelta(days=int(day))
            billScheduleDetails = BillScheduleDetails.objects.filter(start_date=filter_date, last_confirmed=True)
            print billScheduleDetails
            uploadB30 = UploadB30.objects.filter(month=yearMonth, is_deleted=False,
                                                 bill_schedule__in=[bs.billSchedule for bs in
                                                                    billScheduleDetails]).order_by(
                'bill_schedule__bill_cycle__bill_cycle_code')
        else:
            uploadB30 = UploadB30.objects.filter(month=yearMonth, is_deleted=False).order_by(
                'bill_schedule__bill_cycle__bill_cycle_code')

        totalRecords = uploadB30.filter().count()
        print 'billSchedule', uploadB30
        data = {'uploadb30': uploadB30, 'totalRecords': totalRecords}
        print 'data', data
        data = render(request, 'uploadapp/billCyclesTailes.html', data)
    except Exception, e:
        print 'Exception|upload.py|get_bill_cycles_byfilter', e
        data = {'success': 'false', 'message': 'Server Error'}
    return HttpResponse(data)


def load_data():
    try:
        monthYears = []
        for month in range(0, SHOW_MONTH):
            date = datetime.date.today() - dateutil.relativedelta.relativedelta(months=month)
            monthYears.append({'value': str(date.year) + checkMonth(date.month),
                               'text': Months[date.month] + ' ' + str(date.year)})

        uploadb30 = UploadB30.objects.filter(month=monthYears[0]['value'], is_deleted=False).order_by(
            'bill_schedule__bill_cycle__bill_cycle_code')

        consumerDetails = ConsumerDetails.objects.filter(
            bill_cycle__in=[upload.bill_schedule.bill_cycle for upload in uploadb30],
            month=constraints.month_minus(monthYears[0]['value']), is_deleted=False)
        totalConsumerDetails = consumerDetails.filter().count()

        print 'totalConsumerDetails', totalConsumerDetails
        print 'uploadb30.filter()', uploadb30.filter(status='Completed')

        uploadedConsumerCount = consumerDetails.filter(
            bill_cycle__in=[upload.bill_schedule.bill_cycle for upload in uploadb30.filter(status='Completed')],
            is_deleted=False, month=constraints.month_minus(monthYears[0]['value'])).count()
        print '------------------------------------------------------------'

        print 'totalConsumerDetails', totalConsumerDetails
        print 'uploadedConsumerCount', uploadedConsumerCount
        pending = totalConsumerDetails - uploadedConsumerCount

        totalRecords = uploadb30.filter().count()
        notStarted = uploadb30.filter(status='Not Started').count()
        started = uploadb30.filter(status='Started').count()
        failed = uploadb30.filter(status='Failed').count()
        Completed = uploadb30.filter(status='Completed').count()
        print 'billSchedule', uploadb30

        data = {'monthYears': monthYears, 'uploadb30': uploadb30,
                'pending': pending, 'Started': started, 'Failed': failed,
                'uploaded': uploadedConsumerCount, 'Total': totalConsumerDetails,
                'Filters': FILTER_BY,
                'totalRecords': totalRecords
                }
        print data
    except Exception, e:
        print 'Exception|upload.py|load_data', e
        data = {'message': 'Server Error'}
    return data


def checkMonth(month):
    if month > 9:
        return str(month)
    else:
        return '0' + str(month)


# def get_b30_images_url(request, upload_id):
#     try:
#         print '=====================get images url======================='
#         uploadObj = UploadB30.objects.get(id=upload_id)
#         billCycleObj = uploadObj.bill_schedule.bill_cycle
#
#         folderName = 'download/' + billCycleObj.bill_cycle_code + '_' + datetime.datetime.now().strftime(
#             "%d%m%y%H%M%S%s")
#
#         meterReading = MeterReading.objects.filter(jobcard__consumerdetail__bill_cycle=billCycleObj,reading_status='complete',reading_month=uploadObj.month)
#         #zip_source = os.path.join(BASE_DIR, "sitemedia")
#         zip_source = '/sitemedia/'
#         zip_file = billCycleObj.bill_cycle_code + '_' + uploadObj.month + '.zip'
#
#         print '==========len(meterReading)===========',len(meterReading)
#
#         destiFile = zip_source + '/' + folderName
#         if not os.path.exists(destiFile):
#             os.makedirs(destiFile)
#
#         for mr in meterReading:
#             if mr.image_url:
#                 my_file = os.path.join('/sitemedia/', mr.image_url[1:])
#                 #print 'mr', my_file
#                 if os.path.exists(my_file):
#                     copyfile(my_file, destiFile + '/' + mr.jobcard.consumerdetail.consumer_no + '.JPG')
#
#         zipFileName = destiFile
#         shutil.make_archive(zipFileName, 'zip', destiFile)
#         file_name = zipFileName + '.zip'
#         fo = open(file_name, "r")
#
#         print '==========================================dfsf='
#         if os.path.exists(destiFile):
#             shutil.rmtree(destiFile)
#
#         response = HttpResponse(fo, content_type='application/zip')
#         response['Content-Disposition'] = 'attachment; filename=' + zip_file
#
#     except Exception, e:
#         print 'Exception|upload.py|get_Images', e
#         data = {'message': 'Server Error'}
#     return response



def get_b30_images_url(request, upload_id):
    try:
        print 'request In|get_b30_images_url|',upload_id
        uploadObj = UploadB30.objects.get(id=upload_id)
        billCycleObj = uploadObj.bill_schedule.bill_cycle

        folderName = 'download/' + billCycleObj.bill_cycle_code + '_' + datetime.datetime.now().strftime(
            "%d%m%y%H%M%S%s")

        meterReading = MeterReading.objects.filter(jobcard__consumerdetail__bill_cycle=billCycleObj,reading_status='complete',reading_month=uploadObj.month)
        zip_source = '/sitemedia/'
        zip_file = billCycleObj.bill_cycle_code + '_' + uploadObj.month + '.zip'

        destiFile = zip_source + folderName

        if not os.path.exists(destiFile):
            os.makedirs(destiFile)

        for mr in meterReading:
            if mr.image_url:
                my_file = os.path.join('/', mr.image_url[1:])
                if os.path.exists(my_file):
                    copyfile(my_file, destiFile + '/' + mr.jobcard.consumerdetail.consumer_no + '.JPG')

        zipFileName = destiFile
        shutil.make_archive(zipFileName, 'zip', destiFile)
        file_name = zipFileName + '.zip'
        fo = open(file_name, "r")

        if os.path.exists(destiFile):
            shutil.rmtree(destiFile)

        response = HttpResponse(fo, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=' + zip_file

    except Exception, e:
        print 'Exception|upload.py|get_Images', e
        data = {'message': 'Server Error'}
    return response





#
# # unused method uptill now
# @login_required(login_url='/')
# @role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
# def get_b30_images(request, upload_id):
#     try:
#         uploadObj = UploadB30.objects.get(id=upload_id)
#         billCycleObj = uploadObj.bill_schedule.bill_cycle
#
#         jobcads = JobCard.objects.filter(consumerdetail__bill_cycle=billCycleObj, reading_month=uploadObj.month)
#         jobcad_list = [jobcard.id for jobcard in jobcads]
#
#         paths = [os.path.join(BASE_DIR, "sitemedia/meter_reading"),
#                  os.path.join(BASE_DIR, "sitemedia/qr_tempered"),
#                  os.path.join(BASE_DIR, "sitemedia/suspicious_activity")
#                  ]
#
#         zip_source = os.path.join(BASE_DIR, "sitemedia")
#         zip_file = billCycleObj.bill_cycle_code + '_' + uploadObj.month + '.zip'
#         file_to_download = zip_source + '/' + zip_file
#         ZipFile = zipfile.ZipFile(file_to_download, "w")
#
#         for path in paths:
#             files = [f for f in os.listdir(path) if re.match(r'^.*' + uploadObj.month + '.jpg', f)]
#             files_list = []
#
#             for file in files:
#                 file_name = file.split('_')
#                 files_list.append({str(file_name[2]): file})
#
#             print 'files_list', files_list
#
#             rootlen = len(path) + 1
#
#             for jobcrd in jobcad_list:
#                 # print 'jobcrd', jobcrd
#                 for file in files_list:
#                     # print 'files', file
#                     if file.get(str(jobcrd)):
#                         print 'files', file.get(str(jobcrd))
#                         fl = os.path.join(path, file.get(str(jobcrd)))
#                         ZipFile.write(fl, fl[rootlen:], compress_type=zipfile.ZIP_DEFLATED)
#
#         ZipFile.close()
#         print 'ZipFile', ZipFile
#         fo = open(file_to_download, "r")
#         response = HttpResponse(fo, content_type='application/zip')
#         response['Content-Disposition'] = 'attachment; filename=' + zip_file
#
#     except Exception, e:
#         print 'Exception|upload.py|get_Images', e
#         data = {'message': 'Server Error'}
#     return response


def test(request):
    try:
        print 'vikram is here'
        try:
            billObj = BillCycle.objects.get(bill_cycle_code='155516')
        except BillCycle.MultipleObjectsReturned:
            print 'bill cycle multip object'
        obj = RouteDetail.objects.get(billcycle=billObj)
    except RouteDetail.MultipleObjectsReturned:
        obj = RouteDetail.objects.filter(billcycle=billObj).first()
        print obj
    except BillCycle.DoesNotExist:
        print 'bill bycle DoesNotExist======>'

    except Exception, e:
        print 'Exception', e
