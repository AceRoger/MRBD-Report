import json
import pdb
from django.http import HttpResponse
from django.shortcuts import render
import datetime
#from django.conf.settings import GET_ROUTEMASTER_URL, GET_ROUTEDETAILS_URL
from django.conf import settings
#from esselutilities.settings import GET_ROUTEMASTER_URL, GET_ROUTEDETAILS_URL
from consumerapp.models import ConsumerDetails
from scheduleapp.models import BillSchedule, PN33Download
from adminapp.models import City, BillCycle, RT_MASTER, RT_DETAILS, RouteDetail
from suds.client import Client
from celery import task
from django.utils import timezone
from django.db import transaction

from adminapp import constraints

import time

__author__ = 'vkmchandel'


@task
def import_rtmaster(pn33Download):

    try:
        print 'import_rtmaster Task Start with', pn33Download
        print 'settings.GET_ROUTEMASTER_URL',settings.GET_ROUTEMASTER_URL
        print 'settings.GET_ROUTEDETAILS_URL',settings.GET_ROUTEDETAILS_URL

        soapClient_routeMaster = Client(settings.GET_ROUTEMASTER_URL)
        soapClient_routeDetails = Client(settings.GET_ROUTEDETAILS_URL)

        city = pn33Download.bill_schedule.bill_cycle.city.city
        utility = pn33Download.bill_schedule.bill_cycle.utility.utility
        billCycleCode = pn33Download.bill_schedule.bill_cycle.bill_cycle_code
        yearMonth = constraints.month_minus(pn33Download.bill_schedule.month)

        RT_MASTER.objects.filter(BILL_MONTH=yearMonth, BILL_CYC_CD=billCycleCode).delete()
        RT_DETAILS.objects.filter(BILL_CYC_CD=billCycleCode, CURR_MONTH=yearMonth).delete()

        RouteDetail.objects.filter(billcycle=pn33Download.bill_schedule.bill_cycle, month=yearMonth).delete()

        print 'city',city
        print 'utility',utility
        print 'M' + billCycleCode
        print  yearMonth

        soapResponse = soapClient_routeMaster.service.execute(city, utility, 'M' + billCycleCode, yearMonth)
        print 'soapResponse',soapResponse
        time.sleep(60*2)
        rt_masters = RT_MASTER.objects.filter(BILL_MONTH=yearMonth, BILL_CYC_CD=billCycleCode).exclude(ROUTE_ID__isnull=True).exclude(ROUTE_ID__exact='')

        for rt_master in rt_masters:
            if rt_master.ROUTE_ID!="" or rt_master.ROUTE_ID !=None:
                routeDetail = RouteDetail(
                    route_code=rt_master.ROUTE_ID,
                    billcycle=BillCycle.objects.get(bill_cycle_code=rt_master.BILL_CYC_CD),
                    month=rt_master.BILL_MONTH,
                    bill_month=pn33Download.month,
                    created_by='Admin'
                )
                routeDetail.save()
                soapResponse = soapClient_routeDetails.service.execute(city, utility, billCycleCode, rt_master.ROUTE_ID,
                                                                       yearMonth)

        billCycle_obj = BillCycle.objects.get(bill_cycle_code=billCycleCode)
        routeDetails = RouteDetail.objects.filter(billcycle=billCycle_obj, month=yearMonth)

        # validation
        print 'rt_masters.filter().count()=>', rt_masters.filter().count()
        print 'routeDetails.filter().count()=>', routeDetails.filter().count()

        if rt_masters.filter().count() != routeDetails.filter().count():
            raise Exception('rt_master and route details record count is not same')

        print 'import_rtmaster Task Complete with above count'

        import_rtdetails(routeDetails, billCycle_obj, yearMonth, pn33Download,city)


    except Exception, e:
        print 'Exception|task|import_rtmaster', e
        fail_downloadPN33(pn33Download)



def import_rtdetails(routeDetails, billCycle_obj, yearMonth, pn33Download,city):
    try:
        time.sleep(180)

        print 'import_rtdetails Task Start with', routeDetails, billCycle_obj, yearMonth, pn33Download

        ConsumerDetails.objects.filter(bill_cycle=billCycle_obj, month=yearMonth).delete()
        print 'route count from routeDetails==>', routeDetails.filter().count()

        for routeDetail in routeDetails:
            rt_details = RT_DETAILS.objects.filter(BILL_CYC_CD=billCycle_obj.bill_cycle_code,
                                                   ROUTE=routeDetail.route_code, CURR_MONTH=yearMonth)
            print 'RT_DETAILS.count==>', rt_details.filter().count()
            print
            for rt_detail in rt_details:
                consumerDetails = ConsumerDetails(
                    name=rt_detail.CONS_NAME,
                    consumer_no=rt_detail.CONS_NO,
                    email_id='',
                    contact_no='',
                    address_line_1=rt_detail.ADD1,
                    address_line_2=rt_detail.ADD2,
                    address_line_3=rt_detail.ADD3,
                    village=rt_detail.VILLAGE,
                    city=City.objects.get(city=city),
                    pin_code='',
                    route=routeDetail,
                    bill_cycle=billCycle_obj,
                    feeder_code=rt_detail.FEEDER_CD,
                    feeder_name=rt_detail.FEEDER_NAME,
                    meter_no=rt_detail.METER_NO,
                    meter_digit=rt_detail.METER_DIGIT,
                    connection_status=rt_detail.CONS_STATUS,
                    month=rt_detail.CURR_MONTH,
                    bill_month=pn33Download.month,
                    dtc=rt_detail.DTC_CD,
                    dtc_dec=rt_detail.DTC_DESC,
                    pole_no=rt_detail.POLE_NO,

                    prev_feeder_code= rt_detail.PC,
                    prev_reading= rt_detail.CURR_RTG,
                    prev_reading_date= rt_detail.PREVIOUS_RTG_DT,
                    curr_reading_date= rt_detail.CURRENT_RTG_DT,
                    killowatt= rt_detail.LOAD,
                    consumption= '',
                    avg_six_months= rt_detail.AVG,

                    cis_division=rt_detail.CIS_DIVISION,
                    bu=rt_detail.BU,
                    account_id=rt_detail.ACCOUNT_ID,
                    mu_no=rt_detail.MU_NO,
                    fath_hus_name=rt_detail.FATH_HUS_NAME,
                    prev_month=rt_detail.PREV_MONTH,
                    pn33_bill_month=rt_detail.BILL_MONTH,
                    bill_no=rt_detail.BILL_NO,
                    trf_catg=rt_detail.TRF_CATG,
                    conn_date=rt_detail.CONN_DATE,
                    load_unit_cd=rt_detail.LOAD_UNIT_CD,
                    duty_cd=rt_detail.DUTY_CD,
                    urban_flg=rt_detail.URBAN_FLG,
                    area_cd=rt_detail.AREA_CD,
                    area_name=rt_detail.AREA_NAME,
                    sequence=rt_detail.SEQUENCE,
                    gr_no=rt_detail.GR_NO,
                    rd_no=rt_detail.RD_NO,
                    mtr_inst_dt=rt_detail.MTR_INST_DT,
                    mtr_repl_dt=rt_detail.MTR_REPL_DT,
                    meter_phase=rt_detail.METER_PHASE,
                    make=rt_detail.MAKE,
                    mtr_type=rt_detail.MTR_TYPE,
                    mf=rt_detail.MF,
                    prev_rtg=rt_detail.PREV_RTG,
                    curr_rtg=rt_detail.CURR_RTG,
                    curr_rtg_stts=rt_detail.CURR_RTG_STTS,
                    prev_rtg_stts=rt_detail.PREV_RTG_STTS,
                    lcr_unit=rt_detail.LCR_UNIT,

                    lattitude=rt_detail.LATTITUDE,
                    longitude=rt_detail.LONITUDE,
                    created_by='Admin'
                )
                consumerDetails.save()

                # validation
        rt_detiails_count = RT_DETAILS.objects.filter(BILL_CYC_CD=billCycle_obj.bill_cycle_code,
                                                      CURR_MONTH=yearMonth).count()
        consumerDetails_count = ConsumerDetails.objects.filter(bill_cycle=billCycle_obj, month=yearMonth).count()
        if rt_detiails_count != consumerDetails_count:
            raise Exception('rt_detals and ConsumerDetails record count is not same')
        else:
            complete_downloadPN33(pn33Download)
        print 'import_rtmaster Task Complete with Count rt_detiails_count,consumerDetails_count', rt_detiails_count, consumerDetails_count

    except Exception, e:
        print 'Exception|task|import_rtdetails', e
        fail_downloadPN33(pn33Download)
        raise Exception('import_rtddetails has problem')




def fail_downloadPN33(pn33Download):
    try:
        print 'In Task Failed with ', pn33Download
        pn33Download.download_status = 'Failed'
        pn33Download.save()
        yearMonth = constraints.month_minus(pn33Download.bill_schedule.month)

        bill_cycle_code=pn33Download.bill_schedule.bill_cycle.bill_cycle_code
        #RT_MASTER.objects.filter(BILL_MONTH=yearMonth, BILL_CYC_CD=bill_cycle_code).delete()
        #RT_DETAILS.objects.filter(BILL_CYC_CD=bill_cycle_code, CURR_MONTH=yearMonth).delete()
        #RouteDetail.objects.filter(billcycle=pn33Download.bill_schedule.bill_cycle, month=yearMonth).delete()
        #ConsumerDetails.objects.filter(bill_cycle=pn33Download.bill_schedule.bill_cycle, month=yearMonth).delete()

        print 'out Task Failed with ', pn33Download
        return True
    except Exception, e:
        print 'Exception|task.py|fail_downloadPN33', e
    return False


def complete_downloadPN33(pn33Download):
    try:
        print 'In Task Completed with', pn33Download
        pn33Download.download_status = 'Completed'
        pn33Download.end_date = timezone.now()
        print 'Out Task Completed with', pn33Download
        pn33Download.save()

        billSchedule=pn33Download.bill_schedule
        billSchedule.is_imported=True
        billSchedule.save()
        return True
    except Exception, e:
        print 'Exception|task.py|complete_downloadPN33', e
    return False