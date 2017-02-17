import csv
import json
import pdb
from django.http import HttpResponse
from django.shortcuts import render
from adminapp.models import BillCycle
from consumerapp.models import ConsumerDetails, RouteDetail
from django.db.models import Q
from dispatch.models import MeterReading
from scheduleapp.models import BillSchedule

__author__ = 'vkm chandel'


def open_consumer_index(request, bill_schedule_id):
    print 'bill_schedule_id', bill_schedule_id
    billSchedule = BillSchedule.objects.get(id=bill_schedule_id)
    billCycle = billSchedule.bill_cycle
    data = {'routeCodes': RouteDetail.objects.filter(billcycle=billCycle, bill_month=billSchedule.month),
            'billSchedule': billSchedule}

    return render(request, 'consumerapp/consumer.html', data)


def get_consumers_list(request):
    try:
        # pdb.set_trace()
        consumerList = []
        print 'request.GET', request.GET
        column = request.GET.get('order[0][column]')
        searchTxt = request.GET.get('search[value]')
        order = ""

        if request.GET.get('order[0][dir]') == 'desc':
            order = "-"
        list = ['consumer_no', 'name', 'address_line_1', 'contact_no', 'meter_no', 'dtc', 'pole_no']
        column_name = order + list[int(column)]


        start = request.GET.get('start')
        length = int(request.GET.get('length')) + int(request.GET.get('start'))
        route_code = request.GET.get('route_code')
        billSchedule = BillSchedule.objects.get(id=request.GET.get('billSchedule_id'))
        billCycle = billSchedule.bill_cycle

        if route_code == 'All':
            consumerDetails = ConsumerDetails.objects.filter(bill_cycle=billCycle, is_deleted=False,
                                                             bill_month=billSchedule.month)

        else:
            routeDetail = RouteDetail.objects.get(id=route_code)
            consumerDetails = ConsumerDetails.objects.filter(route=routeDetail, bill_cycle=billCycle, is_deleted=False,
                                                             bill_month=billSchedule.month)


        total_record = consumerDetails.filter().count()
        consumerDetails = consumerDetails.filter(
                Q(consumer_no__icontains=searchTxt) | Q(name__icontains=searchTxt) | Q(
                    address_line_1__icontains=searchTxt) | Q(address_line_1__icontains=searchTxt) | Q(
                    address_line_3__icontains=searchTxt)).order_by(
                column_name)[start:length]

        for consumerDetail in consumerDetails:
            tempList = []
            edit = '<a class="fa fa-pencil" style="color: #ed1847;" onclick=viewConsumer(' + str(
                consumerDetail.id) + ') ></a>'

            tempList.append(consumerDetail.consumer_no)
            tempList.append(consumerDetail.name)
            tempList.append(
                consumerDetail.address_line_1 + ',' + consumerDetail.address_line_2 + ',' + consumerDetail.address_line_3)
            tempList.append(consumerDetail.contact_no)
            tempList.append(consumerDetail.meter_no)
            tempList.append(consumerDetail.dtc)
            tempList.append(consumerDetail.pole_no)
            tempList.append(edit)
            consumerList.append(tempList)

        data = {'iTotalRecords': total_record, 'iTotalDisplayRecords': total_record, 'aaData': consumerList}
        print 'data', data
    except Exception, e:
        print 'Exception|consumer.py|load_consumer', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


def reading_export(request, schedule_id):
    try:
        # pdb.set_trace()
        billSchedule = BillSchedule.objects.get(id=schedule_id)
        billCycle = billSchedule.bill_cycle

        consumerDetails = ConsumerDetails.objects.filter(bill_cycle=billCycle, is_deleted=False,
                                                         bill_month=billSchedule.month)

        # response = HttpResponse(content_type='text/csv')
        # response['Content-Disposition'] = 'attachment; filename="readings_for' + str(
        #     billCycle.bill_cycle_code) + '.csv"';
        # # writer = csv.writer(response)
        # writer = csv.writer(response, delimiter='    ', quotechar='"', quoting=csv.QUOTE_ALL)
        # # writer.writerow(['Consumer Number', 'Consumer Name', 'Address', 'Contact No', 'Meter No', 'DTC',
        # #                  'Pole No'])

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="pn33-' + str(billCycle.bill_cycle_code) + '.csv"';
        writer = csv.writer(response)

        writer.writerow(
            ['CIS_DIVISION', 'BILL_CYC_CD', 'BU', 'PC', 'CONS_NO', 'ACCOUNT_ID', 'MU_NO', 'CONS_NAME', 'FATH_HUS_NAME',
             'ADD1', 'ADD2', 'ADD3', 'VILLAGE', 'CITY','PIN_CODE','EMAIL','CONTACT NO','PREV_MONTH', 'BILL_MONTH', 'CURR_MONTH', 'SCHEDULE_MONTH','BILL_NO', 'TRF_CATG',
             'CONN_DATE', 'CONS_STATUS', 'LOAD', 'LOAD_UNIT_CD', 'DUTY_CD', 'URBAN_FLG', 'FEEDER_CD', 'FEEDER_NAME',
             'DTC_CD', 'DTC_DESC', 'AREA_CD', 'AREA_NAME', 'ROUTE', 'SEQUENCE', 'GR_NO', 'RD_NO', 'POLE_NO', 'METER_NO',
             'MTR_INST_DT', 'MTR_REPL_DT', 'METER_PHASE', 'MAKE', 'METER_DIGIT', 'MTR_TYPE', 'MF', 'PREVIOUS_RTG_DT',
             'CURRENT_RTG_DT', 'PREV_RTG', 'CURR_RTG', 'CURR_RTG_STTS', 'PREV_RTG_STTS', 'AVG', 'LCR_UNIT', 'LATTITUDE',
             'LONITUDE'])

        print '=======================list print in========================'

        for consumerDetail in consumerDetails:
            tempList = []
            # tempList.append(str("'") + str(consumerDetail.consumer_no).encode('utf-8'))
            # tempList.append(consumerDetail.name)
            # tempList.append((
            #                 consumerDetail.address_line_1 + ',' + consumerDetail.address_line_2 + ',' + consumerDetail.address_line_3).encode(
            #     'utf-8'))
            # tempList.append(consumerDetail.contact_no)
            # tempList.append(consumerDetail.meter_no)
            # tempList.append(consumerDetail.dtc)
            # tempList.append(consumerDetail.pole_no)


            tempList.append(consumerDetail.cis_division)
            tempList.append(consumerDetail.bill_cycle.bill_cycle_code)
            tempList.append(consumerDetail.bu)
            tempList.append(consumerDetail.prev_feeder_code)
            tempList.append(consumerDetail.consumer_no)
            tempList.append(consumerDetail.account_id)
            tempList.append(consumerDetail.mu_no)
            tempList.append(consumerDetail.name)
            tempList.append(consumerDetail.fath_hus_name)
            tempList.append((consumerDetail.address_line_1).encode('utf-8'))
            tempList.append((consumerDetail.address_line_2).encode('utf-8'))
            tempList.append((consumerDetail.address_line_3).encode('utf-8'))

            #tempList.append(consumerDetail.address_line_1)
            #tempList.append(consumerDetail.address_line_2)
            #tempList.append(consumerDetail.address_line_3)
            tempList.append(consumerDetail.village)
            tempList.append(consumerDetail.city)
            tempList.append(consumerDetail.pin_code)
            #tempList.append(consumerDetail.email_id)
            tempList.append((consumerDetail.email_id).encode('utf-8'))
            tempList.append(consumerDetail.contact_no)
            tempList.append(consumerDetail.prev_month)
            tempList.append(consumerDetail.pn33_bill_month)
            tempList.append(consumerDetail.month)
            tempList.append(consumerDetail.bill_month)
            tempList.append(consumerDetail.bill_no)
            tempList.append(consumerDetail.trf_catg)
            tempList.append(consumerDetail.conn_date)
            tempList.append(consumerDetail.connection_status)
            tempList.append(consumerDetail.killowatt)
            tempList.append(consumerDetail.load_unit_cd)
            tempList.append(consumerDetail.duty_cd)
            tempList.append(consumerDetail.urban_flg)
            tempList.append(consumerDetail.feeder_code)
            tempList.append(consumerDetail.feeder_name)
            tempList.append(consumerDetail.dtc)
            tempList.append(consumerDetail.dtc_dec)
            tempList.append(consumerDetail.area_cd)
            tempList.append(consumerDetail.area_name)
            tempList.append(consumerDetail.route.route_code)
            tempList.append(consumerDetail.sequence)
            tempList.append(consumerDetail.gr_no)
            tempList.append(consumerDetail.rd_no)
            tempList.append(consumerDetail.pole_no)
            tempList.append(consumerDetail.meter_no)
            tempList.append(consumerDetail.mtr_inst_dt)
            tempList.append(consumerDetail.mtr_repl_dt)
            tempList.append(consumerDetail.meter_phase)
            tempList.append(consumerDetail.make)
            tempList.append(consumerDetail.meter_digit)
            tempList.append(consumerDetail.mtr_type)
            tempList.append(consumerDetail.mf)
            tempList.append(consumerDetail.prev_reading_date)
            tempList.append(consumerDetail.curr_reading_date)
            tempList.append(consumerDetail.prev_rtg)
            tempList.append(consumerDetail.curr_rtg)
            tempList.append(consumerDetail.curr_rtg_stts)
            tempList.append(consumerDetail.prev_rtg_stts)
            tempList.append(consumerDetail.avg_six_months)
            tempList.append(consumerDetail.lcr_unit)
            tempList.append(consumerDetail.lattitude)
            tempList.append(consumerDetail.longitude)
            writer.writerow(tempList)
        return response
    except Exception, e:
        print 'Exception|consumer.py|load_consumer', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_consumer_details(request):
    try:

        id = request.GET.get('id')
        consumerDetails = ConsumerDetails.objects.get(id=id)
        data = {
            'name': consumerDetails.name,
            'consumer_no': consumerDetails.consumer_no,
            'email_id': consumerDetails.email_id,
            'contact_no': consumerDetails.contact_no,
            'address': consumerDetails.address_line_1 + ',' + consumerDetails.address_line_2 + consumerDetails.address_line_3 + '\n' + consumerDetails.pin_code,
            'route': consumerDetails.route.route_code,
            'bill_cycle': consumerDetails.bill_cycle.bill_cycle_code,
            'feeder_code': consumerDetails.feeder_code,
            'feeder_name': consumerDetails.feeder_name,
            'dtc': consumerDetails.dtc,
            'pole_no': consumerDetails.pole_no,
            'meter_no': consumerDetails.meter_no,
            'meter_digit': consumerDetails.meter_digit,
            'connection_status': consumerDetails.connection_status,
            'killowatt': consumerDetails.killowatt,
            'success': 'true',
        }
    except Exception, e:
        print 'Exception|pn33|get_consumer_details', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')
