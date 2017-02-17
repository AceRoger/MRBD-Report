import json
from django.http import HttpResponse
from django.shortcuts import render
import datetime
from adminapp.constraints import SHOW_MONTH
from consumerapp.models import RouteDetail, ConsumerDetails
from scheduleapp.models import BillSchedule, PN33Download
from adminapp.models import PN33, City, BillCycle
from xlrd import open_workbook
from django.utils import timezone
from celery import task
from celery.result import AsyncResult
from django.db import transaction

__author__ = 'vkm chandel'

Months = {
    1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR',
    5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG',
    9: 'SPT', 10: 'OCT', 11: 'NOV', 12: 'DEC'}


def open_pn33_index(request):
    data = load_data()
    return render(request, 'consumerapp/pn33.html', data)


# def open_pn33_index01(request):
#     try:
#         monthYears = []
#         for month in range(0, SHOW_MONTH):
#             date = datetime.date.today() - datetime.timedelta(month * 365 / 12)
#             monthYears.append({'value': str(date.year) + checkMonth(date.month),
#                                'text': Months[date.month] + ' ' + str(date.year)})
#
#         print 'month=monthYears[0]', monthYears[0]['value']
#         pn33Downloads = PN33Download.objects.filter(month=monthYears[0]['value'])
#         total = pn33Downloads.filter().count()
#         notStarted = pn33Downloads.filter(download_status='Not Started').count()
#         started = pn33Downloads.filter(download_status='Started').count()
#         failed = pn33Downloads.filter(download_status='Failed').count()
#         Completed = pn33Downloads.filter(download_status='Completed').count()
#         print 'billSchedule', pn33Downloads
#         data = {'monthYears': monthYears, 'pn33Downloads': pn33Downloads,
#                 'NotStarted': notStarted, 'Started': started, 'Failed': failed,
#                 'Completed': Completed, 'Total': total
#                 }
#         print data
#     except Exception, e:
#         print 'Exception', e
#         data = {'message': 'Server Error'}
#     return render(request, 'consumerapp/pn33.html', data)


def load_data():
    try:
        monthYears = []
        for month in range(0, SHOW_MONTH):
            date = datetime.date.today() - datetime.timedelta(month * 365 / 12)
            monthYears.append({'value': str(date.year) + checkMonth(date.month),
                               'text': Months[date.month] + ' ' + str(date.year)})

        if update_download_status(monthYears[0]['value']) == True:
            pn33Downloads = PN33Download.objects.filter(month=monthYears[0]['value'])
            total = pn33Downloads.filter().count()
            notStarted = pn33Downloads.filter(download_status='Not Started').count()
            started = pn33Downloads.filter(download_status='Started').count()
            failed = pn33Downloads.filter(download_status='Failed').count()
            Completed = pn33Downloads.filter(download_status='Completed').count()
            print 'billSchedule', pn33Downloads
            data = {'monthYears': monthYears, 'pn33Downloads': pn33Downloads,
                    'NotStarted': notStarted, 'Started': started, 'Failed': failed,
                    'Completed': Completed, 'Total': total
                    }
            print data
    except Exception, e:
        print 'Exception|pn33.py|load_data', e
        data = {'message': 'Server Error'}
    return data


@transaction.atomic
def update_download_status(month):
    try:
        sid = transaction.savepoint()  # Transaction open
        pn33Downloads = PN33Download.objects.filter(month=month, download_status='Started')
        for started in pn33Downloads:
            if AsyncResult(started.asy_job_id).status == 'SUCCESS' or AsyncResult(started.asy_job_id).ready() == "True":
                started.download_status = 'Completed'
                started.end_date = timezone.now()
                started.save()
        transaction.savepoint_commit(sid)
        return True
    except Exception, e:
        print 'Exception|pn33.py|update_download_status', e
    return False


def import_pn33(request):
    try:
        id = request.GET.get('id')
        taskObject = read_exl.delay(2)
        pn33Download = PN33Download.objects.get(id=id)
        pn33Download.start_date = timezone.now()
        pn33Download.download_status = 'Started'
        pn33Download.asy_job_id = taskObject.task_id
        pn33Download.save()
        data = {'success': 'true'}
    except Exception, e:
        print 'Exception|pn33|import_pn33', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


def stop_importing_pn33(request):
    try:
        id = request.GET.get('id')
        pn33Download = PN33Download.objects.get(id=id)
        pn33Download.start_date = None
        pn33Download.download_status = 'Not Started'
        pn33Download.save()
        data = {'success': 'true'}
    except Exception, e:
        print 'Exception|pn33|import_pn33', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_bill_cycles(request):
    try:
        yearMonth = request.GET.get('yearMonth')
        billCycleList = []
        pn33Downloads = PN33Download.objects.filter(month=yearMonth)
        total = pn33Downloads.filter().count()
        notStarted = pn33Downloads.filter(download_status='Not Started').count()
        started = pn33Downloads.filter(download_status='Started').count()
        failed = pn33Downloads.filter(download_status='Failed').count()
        Completed = pn33Downloads.filter(download_status='Completed').count()
        print 'billSchedule', pn33Downloads

        for pn33Download in pn33Downloads:
            billCycleList.append({
                'id': pn33Download.bill_schedule.bill_cycle.id,
                'billCycleCode': pn33Download.bill_schedule.bill_cycle.bill_cycle_code,
                'download_status': pn33Download.download_status,
                'start_date': pn33Download.bill_schedule.start_date.strftime('%d/%m/%Y'),
                'end_date': pn33Download.bill_schedule.end_date.strftime('%d/%m/%Y'),
                'download_date': pn33Download.end_date.strftime('%d/%m/%Y'),
            })
        data = {'billCycleList': billCycleList,
                'NotStarted': notStarted, 'Started': started, 'Failed': failed,
                'Completed': Completed, 'Total': total, 'success': 'true'
                }
        print data
    except Exception, e:
        print 'Exception|pn33.py|get_bill_cycles', e
        data = {'success': 'false', 'message': 'Server Error'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@task
def read_exl():
    try:
        wb = open_workbook('/home/bynry-01/MyProject/pn33T1.xlsx')
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
        savePn33(values)
        store_consumer('101')
    except Exception, e:
        print 'Exception', e


def store_consumer(billCycle):
    try:
        pn33Details = PN33.objects.filter(LOCCD=billCycle)
        print 'pn33Details', pn33Details
        routeCodes = pn33Details.values('RDNO', 'LOCCD').distinct()
        print 'routeCodes', routeCodes

        for route in routeCodes:
            routeDetail = RouteDetail(
                route_code=route['RDNO'],
                bill_cycle=BillCycle.objects.get(bill_cycle_code=route['LOCCD']),
                created_by='Admin'
            ).save()

        for pn33Detail in pn33Details:
            consumerDetails = ConsumerDetails(
                name=pn33Detail.CONSNAME,
                consumer_no=pn33Detail.CONSNO,
                email_id='',
                contact_no='',
                address_line_1=pn33Detail.ADD1,
                address_line_2=pn33Detail.ADD2,
                city=City.objects.get(city=pn33Detail.CITY),
                pin_code=pn33Detail.PINCODE,
                route=RouteDetail.objects.get(route_code=pn33Detail.RDNO),
                bill_cycle=BillCycle.objects.get(bill_cycle_code=pn33Detail.LOCCD),
                meter_no=pn33Detail.MTRNO,
                dtc=pn33Detail.RDNO,
                pole_no=pn33Detail.POLEPOLEID,
                created_by='Admin'
            ).save()
    except Exception, e:
        print 'Exception=====>', e


def checkMonth(month):
    if month > 9:
        return str(month)
    else:
        return '0' + str(month)


def savePn33(valueLists):
    try:
        for valueList in valueLists:
            pn33 = PN33(LOCCD=valueList[0],
                        CONSNO=valueList[1],
                        BILLMON=valueList[2],
                        BILLNO=valueList[3],
                        CONSNOOLD=valueList[4],
                        FDRSECID=valueList[5],
                        POLELOCCD=valueList[6],
                        POLEPOLEID=valueList[7],
                        LOCDESC=valueList[8],
                        CONSNAME=valueList[9],
                        FATHHUSFLG=valueList[10],
                        FATHHUSNAME=valueList[11],
                        ADD1=valueList[12],
                        ADD2=valueList[13],
                        HNO=valueList[14],
                        MOH=valueList[15],
                        CITY=valueList[16],
                        PINCODE=valueList[17],
                        KHASRAPATTANO=valueList[18],
                        AREAAREAID=valueList[19],
                        AREANAME=valueList[20],
                        URBANFLG=valueList[21],
                        CMPNYNAME=valueList[22],
                        CMPNYTYP=valueList[23],
                        COLNYCOLNYID=valueList[24],
                        CORRADD1=valueList[25],
                        CORRADD2=valueList[26],
                        CORRCITY=valueList[27],
                        CONSNAMEH=valueList[28],
                        CONSADD1H=valueList[29],
                        CONSADD2H=valueList[30],
                        CONSCITYH=valueList[31],
                        CONSMOHH=valueList[32],
                        CONSHNOH=valueList[33],
                        FATHHUSNAMEH=valueList[34],
                        D=valueList[35],
                        DC=valueList[36],
                        GR=valueList[37],
                        GRNO=valueList[38],
                        RD=valueList[39],
                        RDNO=valueList[40],
                        TRFCATG=valueList[41],
                        TRFCATGOLD=valueList[42],
                        DUTYCD=valueList[43],
                        CESSCD=valueList[44],
                        REVCATGCD=valueList[45],
                        LOAD=valueList[46],
                        LOADUNITCD=valueList[47],
                        EMPRBTESCD=valueList[48],
                        DEPTCD=valueList[49],
                        CONNPH=valueList[50],
                        CONNPURCD=valueList[51],
                        CONNTYPCD=valueList[52],
                        CONSCTGCD=valueList[53],
                        BILLPRD=valueList[54],
                        BILLTYPCD=valueList[55],
                        BILLISSUEDATE=valueList[56],
                        FIRSTCASHDUEDATE=valueList[57],
                        FIRSTCHQDUEDATE=valueList[58],
                        PHASECD=valueList[59],
                        INSTFLG=valueList[60],
                        INSTLNO=valueList[61],
                        SDBILLFLG=valueList[62],
                        BILLCORRFLG=valueList[63],
                        SDENHANCFLG=valueList[64],
                        MAINCONSLNK=valueList[65],
                        RDGTYPCD=valueList[66],
                        MTRRNTCD=valueList[67],
                        MTRTYPE=valueList[68],
                        MTRNO=valueList[69],
                        MAKE=valueList[70],
                        MF=valueList[71],
                        CAPACITY=valueList[72],
                        PREVRDG=valueList[73],
                        CURRRDG=valueList[74],
                        ASSCONSMP=valueList[75],
                        MTRCONSMP=valueList[76],
                        CAPACITORCHRG=valueList[77],
                        WELDINGCHRGE=valueList[78],
                        CESS=valueList[79],
                        CURRDEMAND=valueList[80],
                        DUTY=valueList[81],
                        FCA=valueList[82],
                        LOCKCRAMT=valueList[83],
                        ENERGYCHRG=valueList[84],
                        MINCHRG=valueList[85],
                        MTRRENT=valueList[86],
                        OTHCHRG=valueList[87],
                        PREVARR=valueList[88],
                        SURCHARGEARREARS=valueList[89],
                        SDBILLED=valueList[90],
                        SDDUE=valueList[91],
                        SDARREAR=valueList[92],
                        TOTSDHELD=valueList[93],
                        EMPFREEUNIT=valueList[94],
                        EMPFREEFCAUNIT=valueList[95],
                        EMPFREEAMT=valueList[96],
                        EMPFREEFCA=valueList[97],
                        LASTMONTHAV=valueList[98],
                        ADJAMT=valueList[99],
                        TOTALRECEIVEABLE=valueList[100],
                        BILLNET=valueList[101],
                        SURCHRGEDUE=valueList[102],
                        TOTALRECAMTAFTERDUEDT=valueList[103],
                        READAGNCYNAME=valueList[104],
                        MTRREADTAKENBY=valueList[105],
                        TRFRATES=valueList[106],
                        RDGDT=valueList[107],
                        FIXEDCHARGE=valueList[108],
                        CONSSTACD=valueList[109],
                        SPOTBILLFLG=valueList[110],
                        BILLNETDUE1=valueList[111],
                        BILLNETDUE2=valueList[112],
                        BILLNETDUE3=valueList[113],
                        SUBSIDYAMT=valueList[114],
                        ADJGOVT=valueList[115],
                        MISCCHARGE=valueList[116],
                        SDINSTDAYS=valueList[117],
                        SDINSTAMT=valueList[118],
                        SDMTRINSTLBLD=valueList[119],
                        ADVINSTAMT=valueList[120],
                        ADVINSTDAYS=valueList[121],
                        EMPFREEFIXEDCHRG=valueList[122],
                        PWRSVGDEVRBTE=valueList[123],
                        FIXEDCHRGUNITS=valueList[124],
                        CONNDATE=valueList[125],
                        SLNO=valueList[126],
                        MANUID=valueList[127],
                        MTRTYP=valueList[128],
                        MTRINSTDT=valueList[129],
                        MTRREPLDT=valueList[130],
                        VALID=valueList[131])
            pn33.save()
    except Exception, e:
        print 'Exception=======>', e
