import json
from time import timezone
import traceback
import datetime
from django.http import HttpResponse
from django.shortcuts import render
from scheduleapp.models import BillSchedule, PN33Download,BillScheduleDetails,BillScheduleApprovalDetails,UploadB30
from adminapp.models import BillCycle, Utility, City,Zone,Area,ApprovalDetails
from adminapp.constraints import SHOW_MONTH,SERVER_URL
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import pdb
import urllib
import smtplib
import base64
from smtplib import SMTPException
from Crypto.Cipher import AES
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.core.urlresolvers import reverse
import dateutil.relativedelta
from django.contrib.auth.decorators import login_required
from authenticateapp.decorator import role_required


__author__ = 'Mayur_Sable'

Months = {
    1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR',
    5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG',
    9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'}

FILTER_BY=[{'value':'All','text':'All'},
           {'value':'0','text':'Today'},
           {'value':'1','text':'Tomorrow'}]

#TODO Display schedule and summary on screen
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def open_bill_schedule(request):
    try:
        monthYears = []
        for month in range(0, SHOW_MONTH):
            date = datetime.date.today() - dateutil.relativedelta.relativedelta(months=month)
            monthYears.append({'value': str(date.year) + checkMonth(date.month),
                               'text': Months[date.month] + ' ' + str(date.year)})
        yearMonth=str(datetime.date.today().year) + checkMonth(datetime.date.today().month)
        billScheduleDetails = BillScheduleDetails.objects.filter(month=monthYears[0]['value'],is_deleted=False,is_active=True).order_by('billSchedule__bill_cycle__bill_cycle_code')
        copied = billScheduleDetails.filter(is_active=True).count()
        notConfirmed = billScheduleDetails.filter(status='Not Confirmed').count()
        confirmed = billScheduleDetails.filter(status='Confirmed').count()
        pendingApproval = billScheduleDetails.filter(status='Pending Approval').count()
        rejected = billScheduleDetails.filter(status='Rejected').count()
        billCycles = BillCycle.objects.filter(is_deleted=False).order_by('bill_cycle_code')
        city = City.objects.filter(is_deleted=False)
        utility = Utility.objects.filter(is_deleted=False)
        zone_name = Zone.objects.filter(is_deleted=False)
        area_name = Area.objects.filter(is_deleted=False)
        data = {'monthYears': monthYears, 'billSchedules': billScheduleDetails,
                'NotConfirmed': notConfirmed, 'Confirmed': confirmed, 'PendingApproval': pendingApproval,
                'Rejected': rejected, 'Copied': copied,'Filters':FILTER_BY,'yearMonth':yearMonth,
                'BillCycles': billCycles, 'City': city, 'Utility': utility,'Zone': zone_name,'Area': area_name}
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|schedule.py|open_bill_schedule', e
        data = {'message': 'Server Error'}
    return render(request, 'scheduleapp/schedule.html', data)


def checkMonth(month):
    if month > 9:
        return str(month)
    else:
        return '0' + str(month)


#TODO Check Schedule for perticular bill cycle exist or not
@csrf_exempt
@transaction.atomic
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def save_bill_schedule(request):
    print 'Request in with---', request.POST
    if request.method == "POST":
        try:
            sid = transaction.savepoint()  # Transaction open
            billCycle = BillCycle.objects.get(bill_cycle_code=request.POST.get('billCycleCode'))
            if check_exist_schedule(billCycle)=='match' or check_exist_schedule(billCycle)=='error':
                data = {'success': 'avail'}
                return HttpResponse(json.dumps(data), content_type='application/json')
            elif check_existing_schedule(billCycle)=='match' or check_existing_schedule(billCycle)=='error':
                data = {'success': 'exist'}
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                save_schedule(request, billCycle)
                transaction.savepoint_commit(sid)
                data = {'success': 'true'}
                print 'Request in with---',data
        except BillCycle.DoesNotExist:
            sid = transaction.savepoint()  # Transaction open
            billCycle = BillCycle(
                bill_cycle_code=request.POST.get('billCycleCode'),
                city=City.objects.get(city='Muzaffarpur'),
                utility=Utility.objects.get(utility='Electricity'),
                created_by=request.user.email
            )
            billCycle.save()
            save_schedule(request, billCycle)
            transaction.savepoint_commit(sid)
            data = {'success': 'true'}
        except Exception, e:
            print 'exception ', str(traceback.print_exc())
            transaction.rollback(sid)
            print 'Exception|schedule.py|save_bill_schedule', e
            data = {'success': 'false', 'error': 'Exception ' + str(e)}
    else:
        data = {'success': 'false', 'error': 'Method type is not a POST!'}
    return HttpResponse(json.dumps(data), content_type='application/json')

# TODO Check New Bill Schedule is available in Current Month or not
def check_exist_schedule(billCycle):
    try:
        BillSchedule.objects.get(bill_cycle=billCycle,month=str(date.today().year)+checkMonth(date.today().month))
        return 'match'
    except BillSchedule.DoesNotExist:
        return 'not-match'
    except Exception,e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|schedule.py|check_existing_schedule',e
        return 'error'

# TODO Check New Bill Schedule is available in database or not
def check_existing_schedule(billCycle):
    try:
        #BillSchedule.objects.get(bill_cycle=billCycle,month=str(date.today().year)+checkMonth(date.today().month))
        BillSchedule.objects.get(bill_cycle=billCycle,is_uploaded=False)
        return 'match'
    except BillSchedule.DoesNotExist:
        return 'not-match'
    except Exception,e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|schedule.py|check_existing_schedule',e
        return 'error'

# TODO Check New Bill Cycle Code is available in database or not
def check_existing_bllCycle(billCycle):
    try:
        BillCycle.objects.get(bill_cycle_code=billCycle)
        return 'match'
    except BillCycle.DoesNotExist:
        return 'not-match'
    except Exception,e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|schedule.py|check_existing_schedule',e
        return 'error'

#TODO Save schedule and Display on screen
@csrf_exempt
@transaction.atomic
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def save_schedule(request, billCycle):
    try:
        sid = transaction.savepoint()  # Transaction open
        billSchedule = BillSchedule(
            bill_cycle=billCycle,
            month = request.POST.get('billMonth'),
            created_by=request.user.email
        )
        billSchedule.save()
        billScheduleDetails = BillScheduleDetails(
            billSchedule=billSchedule,
            month=billSchedule.month,
            start_date=datetime.datetime.strptime(request.POST.get('startDate'), '%d/%m/%Y'),
            end_date=datetime.datetime.strptime(request.POST.get('endDate'), '%d/%m/%Y'),
            accounting_date=datetime.datetime.strptime(request.POST.get('accountingDate'), '%d/%m/%Y'),
            estimated_date=datetime.datetime.strptime(request.POST.get('estimatedDate'), '%d/%m/%Y'),
            last_confirmed = 'True',
            status = 'Confirmed',
            is_original = 'True',
            is_active ='True',
            created_by=request.user.email
        )
        billScheduleDetails.save()
        pn33Download = PN33Download(
            month=billSchedule.month,
            bill_schedule=billSchedule,
            download_status='Not Started',
            created_by=request.user.email
        )
        pn33Download.save()
        uploadB30 = UploadB30(
            month=billSchedule.month,
            bill_schedule=billSchedule,
            status='Not Started',
            created_by=request.user.email
        )
        uploadB30.save()
        transaction.savepoint_commit(sid)
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        transaction.rollback(sid)
        print 'Exception|schedule.py|save_schedule', e

# TODO Store New Bill Cycle Code
@csrf_exempt
@transaction.atomic
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def save_new_bill_cycle(request):
    print 'Request in save Bill Cycle Code with---',request.POST
    if request.method == "POST":
        try:
            sid = transaction.savepoint()  # Transaction open
            billCycle = request.POST.get('addCycleCode')
            if check_existing_bllCycle(billCycle) == 'match' or check_existing_bllCycle(billCycle) == 'error':
                data = {'success': 'Exist'}
                transaction.savepoint_commit(sid)
                return HttpResponse(json.dumps(data), content_type='application/json')
            elif BillCycle.DoesNotExist:
                sid = transaction.savepoint()  # Transaction open
                billCycle = BillCycle(
                    bill_cycle_code=request.POST.get('addCycleCode'),
                    bill_cycle_name=request.POST.get('addCycleName'),
                    city=City.objects.get(city=request.POST.get('city')),
                    utility=Utility.objects.get(utility=request.POST.get('utility')),
                    zone=Zone.objects.get(zone_name=request.POST.get('zone')),
                    area=Area.objects.get(area_name=request.POST.get('area')),
                    created_by=request.user.email
                )
                billCycle.save()
                transaction.savepoint_commit(sid)
            data = {'success': 'true'}
            print 'Request out save Bill Cycle Code with---',data
        except Exception, e:
            print 'exception ', str(traceback.print_exc())
            transaction.rollback(sid)
            print 'Exception|schedule.py|save_new_bill_cycle', e
            data = {'success': 'false', 'error': 'Exception ' + str(e)}
    else:
        data = {'success': 'false', 'error': 'Method type is not a POST!'}
    return HttpResponse(json.dumps(data), content_type='application/json')


#TODO Schedule copy_from_previous Functionality Start
@csrf_exempt
@transaction.atomic
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def copy_from_previous(request):
    print 'Request in copy_from_previous with---', request.POST
    try:
        sid = transaction.savepoint()  # Transaction open
        currentMonth=request.POST.get('monthYear')
        lastYM=month_minus(currentMonth)
        # currentMonth=get_currentMonthYM()
        billSchedules = BillSchedule.objects.filter(month=lastYM,is_uploaded=True, is_deleted=False).exclude(bill_cycle__in=[schedules.bill_cycle for schedules in BillSchedule.objects.filter(month=currentMonth, is_deleted=False)])
        check = billSchedules.filter().count()
        if check == 0:
            data = {'success': 'Empty'}
        else:
            for bill in billSchedules:
                checkBillSchedule=BillSchedule.objects.filter(bill_cycle=bill.bill_cycle,is_uploaded=False, is_deleted=False)
                if not checkBillSchedule:
                    billScheduleDetails = BillScheduleDetails.objects.get(billSchedule=bill,
                                                                          last_confirmed=True)
                    newBillSchedule = BillSchedule(
                        bill_cycle=bill.bill_cycle,
                        # month=str(date.today().year) + checkMonth(date.today().month)
                        month=currentMonth,
                        created_by=request.user.email
                    )
                    newBillSchedule.save()
                    newBillScheduleDetails = BillScheduleDetails(
                        billSchedule=newBillSchedule,
                        start_date=(billScheduleDetails.start_date + relativedelta(month=date.today().month)),
                        end_date=(billScheduleDetails.end_date + relativedelta(month=date.today().month)),
                        accounting_date=(billScheduleDetails.accounting_date + relativedelta(month=date.today().month)),
                        estimated_date=(billScheduleDetails.estimated_date + relativedelta(month=date.today().month)),
                        month=currentMonth,
                        status='Not Confirmed',
                        version='0',
                        last_confirmed=False,
                        is_original=True,
                        is_active=True,
                        is_deleted=False,
                        created_by=request.user.email
                    )
                    newBillScheduleDetails.save()
                    transaction.savepoint_commit(sid)
                    data = {'success': 'true'}
                else:
                    data = {'success': 'Open'}
            print 'Request out copy_from_previous with---', data
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        transaction.rollback(sid)
        print 'Exception|schedule_py|copy_from_previous', e
        data = {'success': 'false', 'message': 'Server Error'}
    return HttpResponse(json.dumps(data), content_type='application/json')


#TODO Show Edit modal in Not Conformed Tab
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def change_schedule(request):
    print 'Request in Show Edit modal with---', request.GET
    try:
        billScheduleDetails = BillScheduleDetails.objects.get(id=request.GET.get('id'))
        data = {
            'id': request.GET.get('id'),
            'month': billScheduleDetails.billSchedule.month,
            'bill_cycle': billScheduleDetails.billSchedule.bill_cycle.bill_cycle_code,
            'start_date': billScheduleDetails.start_date.strftime('%d/%m/%Y'),
            'estimated_date': billScheduleDetails.estimated_date.strftime('%d/%m/%Y'),
            'end_date': billScheduleDetails.end_date.strftime('%d/%m/%Y'),
            'accounting_date': billScheduleDetails.accounting_date.strftime('%d/%m/%Y'),
            'success': 'true'
        }
        print 'Request out Show Edit modal with---', data
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|schedule_py|change_schedule', e
        data = {'success': 'false', 'message': 'Server Error'}
    return HttpResponse(json.dumps(data), content_type='application/json')


#TODO Save Functionality in Not Conform Schedule
@csrf_exempt
@transaction.atomic
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def save_change_notConformed(request):
    print 'Request in Save Not Conform with---', request.POST
    try:
        if request.method == "POST":
            sid = transaction.savepoint()  # Transaction open
            id = request.POST.get('id')
            schedule_obj = BillScheduleDetails.objects.get(id=id)
            schedule_obj.start_date = datetime.datetime.strptime(request.POST.get('dataStartDate'), '%d/%m/%Y')
            schedule_obj.end_date = datetime.datetime.strptime(request.POST.get('changeEndDate'), '%d/%m/%Y')
            schedule_obj.estimated_date = datetime.datetime.strptime(request.POST.get('dataEstimatedDate'), '%d/%m/%Y')
            schedule_obj.accounting_date = datetime.datetime.strptime(request.POST.get('changeAccountingDate'),
                                                                      '%d/%m/%Y')
            schedule_obj.created_by =request.user.email
            schedule_obj.save()
            change_status(schedule_obj.id,request)
            transaction.savepoint_commit(sid)
            data = {'success': 'true'}
            print 'Request out Save Not Conform with---', data
            return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        transaction.rollback(sid)
        print 'Exception|schedule.py|save_change_notConformed', e
        data = {'success': 'false', 'error': 'Exception ' + str(e)}
    return HttpResponse(json.dumps(data), content_type='application/json')

#TODO Change status from Not_conformed to Conformed
@csrf_exempt
@transaction.atomic
def change_status(id,request):
    try:
        sid = transaction.savepoint()  # Transaction open
        billSchedulesDetails = BillScheduleDetails.objects.get(id=id)
        billSchedulesDetails.status = 'Confirmed'
        billSchedulesDetails.is_original=True
        billSchedulesDetails.last_confirmed=True
        billSchedulesDetails.save()
        pn33Download = PN33Download(
            bill_schedule=billSchedulesDetails.billSchedule,
            download_status='Not Started',
            created_by=request.user.email
        )
        pn33Download.save()
        uploadB30 = UploadB30(
            bill_schedule=billSchedulesDetails.billSchedule,
            status='Not Started',
            created_by=request.user.email
        )
        uploadB30.save()
        transaction.savepoint_commit(sid)
        data = {'success': 'true'}
        print 'Request out with---Status Change'
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        transaction.rollback(sid)
        print 'Exception|schedule_py|change_status', e
        data = {'success': 'false', 'message': 'Server Error'}
    return HttpResponse(json.dumps(data), content_type='application/json')


#TODO Show change modal in Conformed Card
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def change_conformed_tab(request):
    print 'Request change modal in Conform with---', request.GET
    try:
        billSchedules = BillScheduleDetails.objects.get(id=request.GET.get('id'))
        data = {
            'id': request.GET.get('id'),
            'month': billSchedules.billSchedule.month,
            'bill_cycle': billSchedules.billSchedule.bill_cycle.bill_cycle_code,
            'start_date': billSchedules.start_date.strftime('%d/%m/%Y'),
            'estimated_date': billSchedules.estimated_date.strftime('%d/%m/%Y'),
            'end_date': billSchedules.end_date.strftime('%d/%m/%Y'),
            'accounting_date': billSchedules.accounting_date.strftime('%d/%m/%Y'),
            'success': 'true'
        }
        print 'Request change modal out Conform with---',data
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|schedule_py|change_conformed_tab', e
        data = {'success': 'false', 'message': 'Server Error'}
    return HttpResponse(json.dumps(data), content_type='application/json')


#TODO Save Functionality in Conform Card
@csrf_exempt
@transaction.atomic
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def save_conformed_change(request):
    print 'Request save changes in Conform with---',request.POST
    try:
        if request.method == "POST":
            sid = transaction.savepoint()  # Transaction open
            id = request.POST.get('id')
            billScheduleDetailsOld = BillScheduleDetails.objects.get(id=id)
            billScheduleDetailsOld.is_active = False
            billScheduleDetailsOld.save()
            scheduleDetailsNEW = BillScheduleDetails(
                billSchedule=billScheduleDetailsOld.billSchedule,
                start_date=billScheduleDetailsOld.start_date,
                estimated_date=billScheduleDetailsOld.estimated_date,
                month=billScheduleDetailsOld.month,
                end_date=datetime.datetime.strptime(request.POST.get('conformEndDate'),'%d/%m/%Y'),
                accounting_date=datetime.datetime.strptime(request.POST.get('conformAccountingDate'),'%d/%m/%Y'),
                version= int(billScheduleDetailsOld.version) + 1,
                status='Pending Approval',
                is_original=False,
                is_active=True,
                created_by=request.user.email
            )
            scheduleDetailsNEW.save()


            delta = scheduleDetailsNEW.end_date.date() - billScheduleDetailsOld.end_date
            if delta.days == 0:
                accDate = scheduleDetailsNEW.accounting_date.date() - billScheduleDetailsOld.accounting_date
                if accDate.days == 1 or accDate.days == -1:
                    approvalDetails = ApprovalDetails.objects.get(days=abs(accDate.days))
                elif accDate.days == 2 or accDate.days == -2:
                    approvalDetails = ApprovalDetails.objects.get(days=abs(accDate.days))
                else:
                    approvalDetails = ApprovalDetails.objects.get(~Q(days=1),~Q(days=2))

            elif delta.days == 1 or delta.days == -1:
                approvalDetails = ApprovalDetails.objects.get(days=abs(delta.days))
            elif delta.days == 2 or delta.days == -2:
                approvalDetails = ApprovalDetails.objects.get(days=abs(delta.days))
            else:
                approvalDetails = ApprovalDetails.objects.get(~Q(days=1),~Q(days=2))

            billScheduleApprovalDetails = BillScheduleApprovalDetails(
                bill_schedule = scheduleDetailsNEW,
                status = 'Pending Approval',
                send_date = datetime.date.today(),
                approval_details = approvalDetails,
                created_by =request.user.email
            )
            billScheduleApprovalDetails.save()

            email = approvalDetails.approval.email
            send_mail(scheduleDetailsNEW.id, email, request)

        transaction.savepoint_commit(sid)
        data = {'success': 'true'}
        print 'Request save changes out Conform with---',data
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        transaction.rollback(sid)
        print 'Exception|schedule.py|save_conformed_change', e
        data = {'success': 'false', 'error': 'Exception ' + str(e)}
    return HttpResponse(json.dumps(data), content_type='application/json')

#TODO Send mail to Approvar
@csrf_exempt
def send_mail(id,email,request):
    try:
        billSchedule = BillScheduleDetails.objects.get(id=id)
        schedule = billSchedule.billSchedule.bill_cycle.bill_cycle_code
        month = billSchedule.month
        description = request.build_absolute_uri(reverse('schedule:open-approval-index'))
        # description = SERVER_URL+'schedule/approval-Info'
        gmail_user ="training.tungsten@gmail.com"
        gmail_pwd = "Essel@2016"
        FROM =  'Super Admin: <training.tungsten@gmail.com>'
        TO = [email]
        # msg_text = str(id).rjust(32)
        # secret_key = '1234567890123456'  # create new & store somewhere safe
        # cipher = AES.new(secret_key, AES.MODE_ECB)  # never use ECB in strong systems obviously
        # encoded = base64.b64encode(cipher.encrypt(msg_text))

        SUBJECT = "Attention required: Changes in Schedule"
        # TEXT ="Dear Essel User," "\n \n  Admin Edited Bill Schedule.\n  If you want to allow this changes please hit bellow link.\n" +      description + '/?ID=' + encoded + " " + "\n\nThank You,\nEssel Team"
        TEXT = "Dear Essel Approver," "\n\nAdmin has Changed following bill cycle that need your attention.\n\nBill Cycle Code: "+ schedule +"\nBill Month: "+ month +"\n\nPlease approve the changes.\nLink: " + description + "\n\nThank you for your attention.\n\nNote: This is system generated email. If not actioned, next reminder will go to Supervior\n\nRegards,\nMRBD Super Admin"
        server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
        data = {'success': 'true'}
        print 'Request send mail out with---', TO
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception,e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|schedule.py|send_mail', e
        data = {'success': 'true', 'error': 'Exception ' + str(e)}
    return HttpResponse(json.dumps(data), content_type='application/json')

#TODO send Reminder mail to Approvar
@csrf_exempt
def send_Reminder_Mail(request):
    print 'Request in send_Reminder_Mail with---', request.POST
    try:
        billScheduleDetails = BillScheduleDetails.objects.get(id= request.POST.get('id'))
        approvalDetails=BillScheduleApprovalDetails.objects.get(bill_schedule=billScheduleDetails)
        schedule=billScheduleDetails.billSchedule.bill_cycle.bill_cycle_code
        month=billScheduleDetails.month
        email=approvalDetails.approval_details.approval.email
        description = request.build_absolute_uri(reverse('schedule:open-approval-index'))
        gmail_user = "training.tungsten@gmail.com"
        gmail_pwd = "Essel@2016"
        FROM = 'Super Admin: <training.tungsten@gmail.com>'
        TO = [email]
        # id = request.POST.get('id')
        # msg_text = str(id).rjust(32)
        # secret_key = '1234567890123456'  # create new & store somewhere safe
        # cipher = AES.new(secret_key, AES.MODE_ECB)  # never use ECB in strong systems obviously
        # encoded = base64.b64encode(cipher.encrypt(msg_text))
        # SUBJECT = "Reminder mail for approve bill schedule!"
        # TEXT = "Dear Essel User," "\n \n  You are not approve the schedule yet.\n  If you want to allow this changes please hit bellow link.\n" + description + '/?ID=' + encoded + " " + "\n\nThank You,\nEssel Team"
        SUBJECT = "Immediate attention required: Reminder mail for approve schedule!"
        TEXT = "Dear Essel Approver,""\n\nFollowing bill schedule need your immediate attention.\n\nBill Cycle Code: "+ schedule +"\nBill Month: "+ month +"\n\nYou are not approve above bill cycle yet.\nPlease approve the changes.\nLink: " + description +"\n\nThank you for your attention.\n\nNote: This is system generated email. If not actioned, next reminder will go to Supervior\n\nRegards,\nMRBD Super Admin"
        server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
        data = {'success': 'true'}
        print 'Request out send_Reminder_Mail with---',TO
        return HttpResponse(json.dumps(data), content_type='application/json')
    except SMTPException ,e:
        print 'SMTPException ', str(traceback.print_exc())
        print 'SMTPException|schedule.py|send_Reminder_Mail', e
        data = {'success': 'false', 'error': 'Exception ' + str(e)}
    return HttpResponse(json.dumps(data), content_type='application/json')

# TODO Show change modal in Reject Card
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def change_rejected(request):
    print 'Request in change Reject with---', request.GET
    try:
        billSchedules = BillScheduleDetails.objects.get(id=request.GET.get('id'))
        data = {
            'id': request.GET.get('id'),
            'month': billSchedules.billSchedule.month,
            'bill_cycle': billSchedules.billSchedule.bill_cycle.bill_cycle_code,
            'start_date': billSchedules.start_date.strftime('%d/%m/%Y'),
            'estimated_date': billSchedules.estimated_date.strftime('%d/%m/%Y'),
            'end_date': billSchedules.end_date.strftime('%d/%m/%Y'),
            'accounting_date': billSchedules.accounting_date.strftime('%d/%m/%Y'),
            'success': 'true'
        }
        print 'Request out change Reject with---',data
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|schedule_py|change_rejected', e
        data = {'success': 'false', 'message': 'Server Error'}
    return HttpResponse(json.dumps(data), content_type='application/json')


#TODO Save Functionality in Reject Card
@csrf_exempt
@transaction.atomic
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def save_rejected_change(request):
    print 'Request save changes in Reject with---',request.POST
    try:
        if request.method == "POST":
            sid = transaction.savepoint()  # Transaction open
            id = request.POST.get('rejectedSchedule_id')
            billScheduleDetailsOld = BillScheduleDetails.objects.get(id=id)
            billScheduleDetailsOld.is_active = False
            billScheduleDetailsOld.save()

            scheduleDetailsNEW = BillScheduleDetails(
                billSchedule=billScheduleDetailsOld.billSchedule,
                start_date=billScheduleDetailsOld.start_date,
                estimated_date=billScheduleDetailsOld.estimated_date,
                month=billScheduleDetailsOld.month,
                end_date=datetime.datetime.strptime(request.POST.get('rejectedEnd'),'%d/%m/%Y'),
                accounting_date=datetime.datetime.strptime(request.POST.get('rejectedAccounting'),'%d/%m/%Y'),
                version=int(billScheduleDetailsOld.version) + 1,
                status='Pending Approval',
                is_original=False,
                is_active=True,
                created_by=request.user.email
            )
            scheduleDetailsNEW.save()

            delta = scheduleDetailsNEW.end_date.date() - billScheduleDetailsOld.end_date
            if delta.days == 0:
                accDate = scheduleDetailsNEW.accounting_date.date() - billScheduleDetailsOld.accounting_date
                if accDate.days == 1 or accDate.days == -1:
                    approvalDetails = ApprovalDetails.objects.get(days=abs(accDate.days))
                elif accDate.days == 2 or accDate.days == -2:
                    approvalDetails = ApprovalDetails.objects.get(days=abs(accDate.days))
                else:
                    approvalDetails = ApprovalDetails.objects.get(~Q(days=1),~Q(days=2))

            elif delta.days == 1 or delta.days == -1:
                approvalDetails = ApprovalDetails.objects.get(days=abs(delta.days))
            elif delta.days == 2 or delta.days == -2:
                approvalDetails = ApprovalDetails.objects.get(days=abs(delta.days))
            else:
                approvalDetails = ApprovalDetails.objects.get(~Q(days=1),~Q(days=2))

            billScheduleApprovalDetails = BillScheduleApprovalDetails(
                bill_schedule=scheduleDetailsNEW,
                status='Pending Approval',
                send_date=datetime.date.today(),
                approval_details=approvalDetails,
                created_by=request.user.email
            )
            billScheduleApprovalDetails.save()

            email = approvalDetails.approval.email
            send_mail(scheduleDetailsNEW.id, email, request)
            transaction.savepoint_commit(sid)
        data = {'success': 'true'}
        print 'Request save changes out Reject with---',data
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        transaction.rollback(sid)
        print 'Exception|schedule.py|save_rejected_change', e
        data = {'success': 'false', 'error': 'Exception ' + str(e)}
    return HttpResponse(json.dumps(data), content_type='application/json')

#TODO Show History in Conformed Card
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def show_history(request):
    print 'Request Show History in Conformed with---',request.GET
    try:
        Approver=()
        remark=()
        billScheduleDetails = BillScheduleDetails.objects.filter(id=request.GET.get('id'))
        for scheduleDetail in billScheduleDetails:
            schedule={
                'bill_schedule':scheduleDetail.billSchedule.bill_cycle.bill_cycle_code,
                'start_date':scheduleDetail.start_date.strftime('%d/%m/%Y'),
                'end_date':scheduleDetail.end_date.strftime('%d/%m/%Y'),
                'accounting_date':scheduleDetail.accounting_date.strftime('%d/%m/%Y'),
                'estimated_date':scheduleDetail.estimated_date.strftime('%d/%m/%Y'),
            }

        billScheduleApprovalDetails = BillScheduleApprovalDetails.objects.filter(
            bill_schedule=billScheduleDetails, status='Confirmed', is_deleted=False)
        for billScheduleApproval in billScheduleApprovalDetails:
            Approver = billScheduleApproval.approval_details.approval.email,
            remark = billScheduleApproval.remark
        data = {'success': 'true','schedule':schedule,'Approver':Approver,'remark':remark}
        print 'Request show history out Conform with---', data
        return HttpResponse(json.dumps(data), content_type='application/json')

    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|schedule.py|show_history', e
        data = {'success': 'false', 'error': 'Exception ' + str(e)}
    return HttpResponse(json.dumps(data), content_type='application/json')



#TODO Show History in Pending Card
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def pending_history(request):
    print 'Request Show History in Pending with---', request.GET
    try:
        billScheduleDetails = BillScheduleDetails.objects.get(id=request.GET.get('id'))
        scheduleDetails = BillScheduleDetails.objects.filter(billSchedule=billScheduleDetails.billSchedule,is_deleted=False)
        changes_list=[]
        for schedule in scheduleDetails.filter().exclude(is_original=True):
            changes_list.append({
                'change_end_date': schedule.end_date.strftime('%d/%m/%Y'),
                'change_accounting_date': schedule.accounting_date.strftime('%d/%m/%Y'),
                'status':schedule.status,

            })

        for schedule in scheduleDetails.filter(is_original=True):
            get_original={
                'bill_cycle': schedule.billSchedule.bill_cycle.bill_cycle_code,
                'start_date':schedule.start_date.strftime('%d/%m/%Y'),
                'end_date':schedule.end_date.strftime('%d/%m/%Y'),
                'accounting_date':schedule.accounting_date.strftime('%d/%m/%Y'),
                'estimated_date':schedule.estimated_date.strftime('%d/%m/%Y'),
            }
        data = {'success': 'true','get_original':get_original,'changes_list':changes_list}
        print 'Request show history out Pending with---', data
        return HttpResponse(json.dumps(data), content_type='application/json')

    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|schedule.py|pending_history', e
        data = {'success': 'false', 'error': 'Exception ' + str(e)}
    return HttpResponse(json.dumps(data), content_type='application/json')

#TODO Show History in Reject Card
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def rejected_history(request):
    print 'Request Show History in Reject with---', request.GET
    try:
        billScheduleDetails = BillScheduleDetails.objects.get(id=request.GET.get('id'))
        billScheduleApprovalDetails = BillScheduleApprovalDetails.objects.filter(
            bill_schedule=billScheduleDetails, status='Rejected', is_deleted=False)
        for billScheduleApproval in billScheduleApprovalDetails:
            billDetails = {
                'Approver': billScheduleApproval.approval_details.approval.email,
                'remark': billScheduleApproval.remark
            }
        scheduleDetails = BillScheduleDetails.objects.filter(billSchedule=billScheduleDetails.billSchedule,
                                                             is_deleted=False)
        for schedule in scheduleDetails.filter().exclude(is_original=True):
            changes_list ={
                'extended_end_date': schedule.end_date.strftime('%d/%m/%Y'),
                'extended_accounting_date': schedule.accounting_date.strftime('%d/%m/%Y'),
            }
        for schedule in scheduleDetails.filter(is_original=True):
            details={
                'month': schedule.billSchedule.month,
                'bill_cycle': schedule.billSchedule.bill_cycle.bill_cycle_code,
                'start_date':schedule.start_date.strftime('%d/%m/%Y'),
                'end_date':schedule.end_date.strftime('%d/%m/%Y'),
                'accounting_date':schedule.accounting_date.strftime('%d/%m/%Y'),
                'estimated_date':schedule.estimated_date.strftime('%d/%m/%Y'),
            }
        data = {'success': 'true','details':details,'billDetails':billDetails,'changes_list':changes_list}
        print 'Request show history out Reject with---', data
        return HttpResponse(json.dumps(data), content_type='application/json')

    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|schedule.py|rejected_history', e
        data = {'success': 'false', 'error': 'Exception ' + str(e)}
    return HttpResponse(json.dumps(data), content_type='application/json')


#TODO Display Data on month year filter
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_bill_schedules(request):
    print 'Request in month year filter with---', request.GET
    try:
        yearMonth=request.GET.get('yearMonth')
        billScheduleDetails = BillScheduleDetails.objects.filter(month=yearMonth,is_deleted=False,is_active=True).order_by('billSchedule__bill_cycle__bill_cycle_code')
        copied = billScheduleDetails.filter(is_active=True).count()
        notConfirmed = billScheduleDetails.filter(status='Not Confirmed').count()
        confirmed = billScheduleDetails.filter(status='Confirmed').count()
        pendingApproval = billScheduleDetails.filter(status='Pending Approval').count()
        rejected = billScheduleDetails.filter(status='Rejected').count()
        yearMonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month)
        data = {'billSchedules': billScheduleDetails,
                'NotConfirmed': notConfirmed, 'Confirmed': confirmed, 'PendingApproval': pendingApproval,
                'Rejected': rejected, 'Copied': copied,'yearMonth':yearMonth
                }
        data=render(request,'scheduleapp/scheduleBody.html',data)
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|schedule.py|get_bill_schedules', e
        data = {'message': 'Server Error'}
    return HttpResponse(data)

#TODO Display Data according filter by
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_bill_schedules_byfilter(request):
    print 'Request in month year filter with---', request.GET
    try:
        yearMonth=request.GET.get('yearMonth')
        day=request.GET.get('filterBy')
        if day!='All':
            filter_date = datetime.date.today() + datetime.timedelta(days=int(day))
            billScheduleDetails = BillScheduleDetails.objects.filter(start_date=filter_date, month=yearMonth, is_deleted=False, is_active=True).order_by('billSchedule__bill_cycle__bill_cycle_code')
        else:
            billScheduleDetails = BillScheduleDetails.objects.filter(month=yearMonth, is_deleted=False, is_active=True).order_by('billSchedule__bill_cycle__bill_cycle_code')

        copied = billScheduleDetails.filter(is_active=True).count()
        data = {'billSchedules': billScheduleDetails,'Copied': copied,'day':day}
        data=render(request,'scheduleapp/scheduleBody.html',data)
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|schedule.py|get_bill_schedules_byfilter', e
        data = {'message': 'Server Error'}
    return HttpResponse(data)


def get_lastMonthYM():
    try:
        today = date.today()
        first = today.replace(day=1)
        lastMonth = first - datetime.timedelta(days=1)
        return lastMonth.strftime("%Y%m")
    except Exception,e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|schedule|get_lastMonth',e
        return None

def get_currentMonthYM():
    try:
        today = date.today()
        return today.strftime("%Y%m")
    except Exception,e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|schedule|get_lastMonth',e
        return None

def month_minus(currentMonth):
    try:
        year=int(currentMonth[:-2])
        month=int(currentMonth[-2:])

        if month==1:
            year=year-1
            month=12
        else:
            month=month-1
        return str(year)+checkMonth(month)
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|task.py|fail_downloadPN33', e
    return None