import csv
import json
import pdb
from django.http import HttpResponse
from django.shortcuts import render
import datetime
from django.db.models import Q
from consumerapp.models import ConsumerDetails,UnBilledConsumers
from dispatch.models import MeterStatus,RouteAssignment,JobCard,ReaderStatus,MeterReading, ValidatorAssignment, UnbilledConsumerAssignment, UnbilledConsumerAssignmentCount, ValidatorAssignmentCount
from scheduleapp.models import BillSchedule, PN33Download, UploadB30, BillScheduleDetails
from adminapp.models import City, BillCycle, RT_MASTER, RT_DETAILS, RouteDetail, UserProfile
from meterreaderapp.models import DeviceDetail
from suds.client import Client
import traceback

def get_dump01(request,bill_month,bill_cycle_code):
    try:
        reading=''
        data={}
        billCycle=BillCycle.objects.get(bill_cycle_code=bill_cycle_code,is_deleted=False)

        consumerDetails=ConsumerDetails.objects.filter(bill_cycle=billCycle,bill_month=bill_month,is_deleted=False)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Details_for' + str(bill_cycle_code) + '.csv"';
        writer = csv.writer(response)
        # writer = csv.writer(response, delimiter='	', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(
            ['BILL_CYC_CD', 'BILL_MONTH', 'ROUTE_CODE', 'CONSUMER_NO', 'ADDRESS1', 'METER_NO',
             'PREV_READING', 'PREV_READING_DATE', 'PREV_RTG_STTS',
             'CURRENT_MT_READING', 'CURRENT_MT_RDG_V1', 'CURRENT_MT_RDG_V2', 'CONSUMPTION', 'METER_STS', 'METER_STS_V1',
             'METER_STS_V2', 'READER_STS', 'READER_STS_V1',  'READER_STS_V2', 'REMARK', 'REMARK_V1', 'REMARK_V2',
             'IMG_REMARK_V1', 'IMG_REMARK_V2', 'READING_DATE', 'VALIDATOR1_DATE','VALIDATOR2_DATE', 'LATTITUDE',
             'LONGITUDE', 'METER_READER_ID', 'METER_READER_NAME', 'VALIDATOR1_NAME', 'VALIDATOR2_NAME', 'READING STATUS',
             'RD_TAKEN_BY'])

        for consumer in consumerDetails:
            tempList=[]
            list=[]
            readings = MeterReading.objects.filter(jobcard__consumerdetail=consumer,
                                               jobcard__consumerdetail__bill_cycle=billCycle, reading_month=bill_month,is_deleted=False)
            if readings:
                for reading in readings:

                    validatorAssignment1=ValidatorAssignment.objects.filter(meterreading=reading,assigned_to='validator1').first()
                    validatorAssignment2 = ValidatorAssignment.objects.filter(meterreading=reading,assigned_to='validator2').first()
                    v1_name=""
                    v2_name=""
                    if validatorAssignment1:
                        v1_name=validatorAssignment1.user.first_name

                    if validatorAssignment2:
                        v2_name=validatorAssignment2.user.first_name


                    tempList.append(bill_cycle_code)
                    tempList.append(bill_month)
                    tempList.append((consumer.route_code).encode('utf-8'))
                    tempList.append((consumer.consumer_no).encode('utf-8'))
                    tempList.append((consumer.address_line_1).encode('utf-8'))
                    tempList.append((consumer.meter_no).encode('utf-8'))
                    tempList.append(consumer.name)
                    # tempList.append(consumer.prev_reading_date)
                    tempList.append(reading.current_meter_reading)
                    tempList.append(reading.meter_status)
                    tempList.append(reading.reader_status)
                    tempList.append(reading.comment)
                    tempList.append(reading.suspicious_activity)
                    tempList.append(reading.suspicious_activity_remark)
                    tempList.append(reading.latitude)
                    tempList.append(reading.longitude)
                    tempList.append(reading.meterreader.employee_id)
                    tempList.append(reading.comment_v2)
                    tempList.append(reading.current_meter_reading_v2)
                    tempList.append(reading.meter_status)
                    tempList.append(reading.reader_status)
                    tempList.append(reading.jobcard.meterreader.employee_id)
                    tempList.append(reading.jobcard.meterreader.first_name + '  ' +reading.jobcard.meterreader.last_name)
                    tempList.append(v1_name)
                    tempList.append(v2_name)
                    tempList.append(reading.comment)
                    tempList.append(reading.reading_date.strftime('%d-%m-%Y'))
                    tempList.append(reading.reading_taken_by)
                    tempList.append(reading.image_remark_v1)
                    tempList.append(reading.image_remark_v2)

                    writer.writerow(tempList)
                    # print "====tempList==",tempList
            else:
                list.append(bill_cycle_code)
                list.append(bill_month)
                list.append((consumer.route.route_code).encode('utf-8'))
                list.append((consumer.consumer_no).encode('utf-8'))
                list.append((consumer.address_line_1).encode('utf-8'))
                list.append((consumer.meter_no).encode('utf-8'))
                list.append(consumer.prev_reading)
                list.append(consumer.prev_reading_date)
                list.append(consumer.prev_rtg_stts)
                list.append('')
                list.append('')
                list.append('')
                list.append('')
                list.append('')
                list.append('')
                list.append('')
                list.append('')
                list.append('')
                list.append('')
                list.append('')
                list.append('')
                list.append('')
                list.append('')
                list.append('')
                list.append('')
                list.append('')
                list.append('')
                list.append('')
                list.append('')
                list.append('')
                list.append('')

                writer.writerow(list)
                # print "=======list=========",list
        data = {'message': 'Server Success'}
        return response
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|helper.py|get_dump', e
        data = {'message': 'Server Error'}
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_dump(request,bill_month,bill_cycle_code):
    try:

        billCycle = BillCycle.objects.get(bill_cycle_code=bill_cycle_code, is_deleted=False)

        consumerDetails = ConsumerDetails.objects.filter(bill_cycle=billCycle, is_deleted=False,
                                                         bill_month=bill_month)

        meterReadings = MeterReading.objects.filter(jobcard__consumerdetail__bill_cycle=billCycle,
                                                    reading_month=bill_month, is_active=False)

        # due_data = billScheduleDetails.end_date.strftime('%d/%m/%Y')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="readings_for' + str(bill_cycle_code) + '.csv"';
        writer = csv.writer(response)
        writer.writerow(
            ['BILL_CYC_CD', 'BILL_MONTH', 'ROUTE_CODE', 'CONSUMER_NO','CONSUMER_NAME', 'ADDRESS1', 'METER_NO',
             'PREV_READING', 'PREV_READING_DATE', 'PREV_RTG_STTS', 'READING STATUS',
             'CURRENT_MT_READING', 'CURRENT_MT_RDG_V1', 'CURRENT_MT_RDG_V2', 'CONSUMPTION', 'METER_STS', 'METER_STS_V1',
             'METER_STS_V2', 'READER_STS', 'READER_STS_V1',  'READER_STS_V2', 'REMARK', 'REMARK_V1', 'REMARK_V2',
             'IMG_REMARK_V1', 'IMG_REMARK_V2','SUSPICIOUS_ACTIVITY','SUSPICIOUS_ACTIVITY_REMARK', 'READING_DATE', 'VALIDATOR1_DATE','VALIDATOR2_DATE', 'LATTITUDE',
             'LONGITUDE', 'METER_READER_ID', 'METER_READER_NAME', 'VALIDATOR1_NAME', 'VALIDATOR2_NAME',
             'RD_TAKEN_BY','DUPICATE'])



        meterReading = meterReadings.filter(is_active=False)

        for reading_status in meterReading:
            tempList = []
            consumerDetail = ConsumerDetails.objects.get(id=reading_status.jobcard.consumerdetail.id, bill_cycle=billCycle, is_deleted=False,bill_month=bill_month)

            # print "consumerDetail=========>",consumerDetail
            tempList.append(bill_cycle_code)
            tempList.append(bill_month)
            tempList.append(consumerDetail.route.route_code)
            #tempList.append("'" + str(consumerDetail.consumer_no))
            tempList.append("'" + str(consumerDetail.consumer_no))
            tempList.append(consumerDetail.name)
            tempList.append((consumerDetail.address_line_1).encode('utf-8'))
            tempList.append(consumerDetail.meter_no)


            pre_reading=consumerDetail.prev_reading

            tempList.append(consumerDetail.prev_reading)

            if consumerDetail.prev_reading_date:
                tempList.append(consumerDetail.prev_reading_date.strftime("%d/%m/%Y"))
            else:
                tempList.append('----')

            #tempList.append(consumerDetail.mf)

            if consumerDetail.mf:
                try:
                    meterStatus=MeterStatus.objects.get(status_code=consumerDetail.mf)
                    tempList.append(meterStatus.meter_status)
                except:
                    tempList.append('----')
            else:
                tempList.append('----')


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

            #----consumption Calculation-----

            if reading_status:
                if reading_status.current_meter_reading_v2:
                    currentReading=reading_status.current_meter_reading_v2
                elif reading_status.current_meter_reading_v1:
                    currentReading=reading_status.current_meter_reading_v1
                else:
                    currentReading=reading_status.current_meter_reading

                #print 'currentReading==>',currentReading
                #print 'pre_reading==>',pre_reading

                try:
                    consumption=float(currentReading)-float(pre_reading)
                    tempList.append(consumption)
                except:
                    tempList.append('----')

                #print 'consumption========',consumption

            else:
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
                tempList.append(reading_status.comment)
                tempList.append(reading_status.comment_v1)
                tempList.append(reading_status.comment_v2)
                tempList.append(reading_status.image_remark_v1)
                tempList.append(reading_status.image_remark_v2)

                if reading_status.suspicious_activity==True:
                    tempList.append('Yes')
                else:
                    tempList.append('No')
                tempList.append(reading_status.suspicious_activity_remark)
            else:
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')



            if reading_status:
                if reading_status.reading_date:
                    tempList.append(reading_status.reading_date.strftime("%d/%m/%Y"))
                else:
                    tempList.append('----')

                if reading_status.validated_on_v1:
                    tempList.append(reading_status.validated_on_v1.strftime("%d/%m/%Y"))
                else:
                    tempList.append('----')

                if reading_status.validated_on_v2:
                    tempList.append(reading_status.validated_on_v2.strftime("%d/%m/%Y"))
                else:
                    tempList.append('----')

                tempList.append(reading_status.latitude)
                tempList.append(reading_status.longitude)
            else:
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')

            if reading_status:
                if reading_status.jobcard.meterreader:
                    tempList.append(reading_status.jobcard.meterreader.employee_id)
                    tempList.append(reading_status.jobcard.meterreader.first_name+' '+reading_status.jobcard.meterreader.last_name)
                else:
                    tempList.append('---')
                    tempList.append('---')

                if reading_status.updated_by_v1:
                    tempList.append(reading_status.updated_by_v1.first_name+' '+reading_status.updated_by_v1.last_name)
                else:
                    tempList.append('---')

                if reading_status.updated_by_v2:
                    tempList.append(reading_status.updated_by_v2.first_name+' '+reading_status.updated_by_v2.last_name)
                else:
                    tempList.append('---')
                tempList.append(reading_status.reading_taken_by)

                if reading_status.is_duplicate==True:
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
        print 'Exception|helper.py|get_dump', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_unbilled_consumers(request,bill_month,bill_cycle_code):
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="UnBilledConsumers_Details_for' + str(bill_cycle_code) + '.csv"';
        writer = csv.writer(response)
        # writer = csv.writer(response, delimiter='	', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(
            ['BILL_MONTH', 'BILL_CYC_CD', 'ROUTE_CODE', 'CONSUMER_NO', 'CONSUMER_NAME', 'READING_STATUS',
             'CURRENT_MT_READING', 'METER_STS', 'READER_STS', 'REMARK', 'SUSPICIOUS_ACTIVITY','SUSPICIOUS_ACTIVITY_REMARK',
             'LATTITUDE', 'LONGITUDE', 'METER_READER_ID', 'METER_READER_NAME', 'READING_DATE'])

        unBilledConsumers=UnBilledConsumers.objects.filter(reading_month=bill_month,bill_cycle_code=bill_cycle_code)
        # print "unBilledConsumers=========>",unBilledConsumers
        for consumers in unBilledConsumers:
            tempList=[]
            tempList.append(bill_month)
            tempList.append(bill_cycle_code)
            tempList.append(consumers.route_code)
            tempList.append(consumers.consumer_no)
            tempList.append(consumers.name)

            if consumers.is_confirmed== True and consumers.is_descarded== False:
                tempList.append('Confirmed')
            elif consumers.is_confirmed == False and consumers.is_descarded == True:
                tempList.append('Discarded')
            else:
                tempList.append('Pending')

            tempList.append(consumers.current_meter_reading)
            tempList.append(consumers.meter_status)
            tempList.append(consumers.reader_status)
            tempList.append(consumers.comment)
            if consumers.suspicious_activity==True:
                tempList.append('Yes')
            else:
                tempList.append('No')
            tempList.append(consumers.suspicious_activity_remark)
            tempList.append(consumers.latitude)
            tempList.append(consumers.longitude)
            tempList.append(consumers.meterreader.employee_id)
            if consumers.meterreader:
                tempList.append(consumers.meterreader.first_name + ' ' + consumers.meterreader.last_name)
            else:
                tempList.append('---')

            if consumers.reading_date:
                tempList.append(consumers.reading_date.strftime('%d-%m-%Y'))
            else:
                tempList.append('----')
            # tempList.append(consumers.reading_taken_by)
            writer.writerow(tempList)
        return response
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|helper.py|unbilled_consumers', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')




def get_all_consumer(request,bill_month,from_date,to_date):
    try:

        # billCycle = BillCycle.objects.get(bill_cycle_code=bill_cycle_code, is_deleted=False)
        #
        # consumerDetails = ConsumerDetails.objects.filter(bill_cycle=billCycle, is_deleted=False,
        #                                                  bill_month=bill_month)

        year=str(from_date)[:4]
        month=str(from_date)[4:6]
        date=str(from_date)[6:8]
        From_date = year+'-'+month+'-'+date+' 00:00:00'
        tyear = str(to_date)[:4]
        tmonth = str(to_date)[4:6]
        tdate = str(to_date)[6:8]
        To_date = tyear+'-'+tmonth+'-'+tdate+' 00:00:00'
        meterReadings = MeterReading.objects.filter(reading_month=bill_month,created_on__gte=From_date,created_on__lte=To_date)

        # print "****************meterReadings**********************",meterReadings
        # due_data = billScheduleDetails.end_date.strftime('%d/%m/%Y')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Dump_of_All_Consumer_for_month_' + str(bill_month) + '.csv"';
        writer = csv.writer(response)
        writer.writerow(
            ['BILL_CYC_CD', 'BILL_MONTH', 'ROUTE_CODE', 'CONSUMER_NO','CONSUMER_NAME', 'ADDRESS1', 'METER_NO',
             'PREV_READING', 'PREV_READING_DATE', 'PREV_RTG_STTS', 'READING STATUS',
             'CURRENT_MT_READING', 'CURRENT_MT_RDG_V1', 'CURRENT_MT_RDG_V2', 'CONSUMPTION', 'METER_STS', 'METER_STS_V1',
             'METER_STS_V2', 'READER_STS', 'READER_STS_V1',  'READER_STS_V2', 'REMARK', 'REMARK_V1', 'REMARK_V2',
             'IMG_REMARK_V1', 'IMG_REMARK_V2','SUSPICIOUS_ACTIVITY','SUSPICIOUS_ACTIVITY_REMARK', 'READING_DATE', 'VALIDATOR1_DATE','VALIDATOR2_DATE', 'LATTITUDE',
             'LONGITUDE', 'METER_READER_ID', 'METER_READER_NAME', 'VALIDATOR1_NAME', 'VALIDATOR2_NAME',
             'RD_TAKEN_BY','DUPICATE'])



        # meterReading = meterReadings.filter(is_active=False)

        for reading_status in meterReadings:
            tempList = []
            consumerDetail = ConsumerDetails.objects.get(id=reading_status.jobcard.consumerdetail.id, is_deleted=False,bill_month=bill_month)

            # print "consumerDetail=========>",consumerDetail
            tempList.append(consumerDetail.bill_cycle.bill_cycle_code)
            tempList.append(bill_month)
            tempList.append(consumerDetail.route.route_code)
            #tempList.append("'" + str(consumerDetail.consumer_no))
            tempList.append("'" + str(consumerDetail.consumer_no))
            tempList.append(consumerDetail.name)
            tempList.append((consumerDetail.address_line_1).encode('utf-8'))
            tempList.append(consumerDetail.meter_no)


            pre_reading=consumerDetail.prev_reading

            tempList.append(consumerDetail.prev_reading)

            if consumerDetail.prev_reading_date:
                tempList.append(consumerDetail.prev_reading_date.strftime("%d/%m/%Y"))
            else:
                tempList.append('----')

            #tempList.append(consumerDetail.mf)

            if consumerDetail.mf:
                try:
                    meterStatus=MeterStatus.objects.get(status_code=consumerDetail.mf)
                    tempList.append(meterStatus.meter_status)
                except:
                    tempList.append('----')
            else:
                tempList.append('----')


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

            #----consumption Calculation-----

            if reading_status:
                if reading_status.current_meter_reading_v2:
                    currentReading=reading_status.current_meter_reading_v2
                elif reading_status.current_meter_reading_v1:
                    currentReading=reading_status.current_meter_reading_v1
                else:
                    currentReading=reading_status.current_meter_reading

                #print 'currentReading==>',currentReading
                #print 'pre_reading==>',pre_reading

                try:
                    consumption=float(currentReading)-float(pre_reading)
                    tempList.append(consumption)
                except:
                    tempList.append('----')

                #print 'consumption========',consumption

            else:
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
                tempList.append(reading_status.comment)
                tempList.append(reading_status.comment_v1)
                tempList.append(reading_status.comment_v2)
                tempList.append(reading_status.image_remark_v1)
                tempList.append(reading_status.image_remark_v2)

                if reading_status.suspicious_activity==True:
                    tempList.append('Yes')
                else:
                    tempList.append('No')
                tempList.append(reading_status.suspicious_activity_remark)
            else:
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')



            if reading_status:
                if reading_status.reading_date:
                    tempList.append(reading_status.reading_date.strftime("%d/%m/%Y"))
                else:
                    tempList.append('----')

                if reading_status.validated_on_v1:
                    tempList.append(reading_status.validated_on_v1.strftime("%d/%m/%Y"))
                else:
                    tempList.append('----')

                if reading_status.validated_on_v2:
                    tempList.append(reading_status.validated_on_v2.strftime("%d/%m/%Y"))
                else:
                    tempList.append('----')

                tempList.append(reading_status.latitude)
                tempList.append(reading_status.longitude)
            else:
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')
                tempList.append('----')

            if reading_status:
                if reading_status.jobcard.meterreader:
                    tempList.append(reading_status.jobcard.meterreader.employee_id)
                    tempList.append(reading_status.jobcard.meterreader.first_name+' '+reading_status.jobcard.meterreader.last_name)
                else:
                    tempList.append('---')
                    tempList.append('---')

                if reading_status.updated_by_v1:
                    tempList.append(reading_status.updated_by_v1.first_name+' '+reading_status.updated_by_v1.last_name)
                else:
                    tempList.append('---')

                if reading_status.updated_by_v2:
                    tempList.append(reading_status.updated_by_v2.first_name+' '+reading_status.updated_by_v2.last_name)
                else:
                    tempList.append('---')
                tempList.append(reading_status.reading_taken_by)

                if reading_status.is_duplicate==True:
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
            # print "***********tempList**************",tempList
        return response
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|helper.py|get_all_consumer', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')
