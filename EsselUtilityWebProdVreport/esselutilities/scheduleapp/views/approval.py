import json
import datetime
from django.shortcuts import render
from scheduleapp.models import BillSchedule, BillScheduleDetails, BillScheduleApprovalDetails
from adminapp.models import BillCycle, ApprovalDetails
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q
import pdb
import traceback
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from authenticateapp.decorator import role_required

__author__ = 'Mayur_Sable'

Months = {
    '01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR',
    '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AUG',
    '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'}


@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Approve schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def open_approval_index(request):
    return render(request, 'scheduleapp/approval.html')


@csrf_exempt
@transaction.atomic
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Approve schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def approval_list(request):
    try:
        userRoleList = []
        column = request.GET.get('order[0][column]')
        searchTxt = request.GET.get('search[value]')
        order = ""
        if request.GET.get('order[0][dir]') == 'desc':
            order = "-"
        list = ['bill_schedule__billSchedule__bill_cycle__bill_cycle_code']
        column_name = order + list[int(column)]
        start = request.GET.get('start')
        length = int(request.GET.get('length')) + int(request.GET.get('start'))
        approvalDetails = ApprovalDetails.objects.get(approval=request.user)
        total_record = BillScheduleApprovalDetails.objects.filter(
            Q(bill_schedule__billSchedule__bill_cycle__bill_cycle_code__icontains=searchTxt), approval_details=approvalDetails,
            status="Pending Approval", is_deleted=False).count()
        billScheduleDetails = BillScheduleApprovalDetails.objects.filter(
            Q(bill_schedule__billSchedule__bill_cycle__bill_cycle_code__icontains=searchTxt), approval_details=approvalDetails,
            is_deleted=False, status="Pending Approval").order_by(column_name)[start:length]
        for scheduleDetail in billScheduleDetails:
            tempList = []
            tempList.append(scheduleDetail.bill_schedule.billSchedule.bill_cycle.bill_cycle_code)
            tempList.append(scheduleDetail.bill_schedule.billSchedule.bill_cycle.bill_cycle_name)
            tempList.append(scheduleDetail.send_date.strftime('%d/%m/%Y'))
            month = Months[scheduleDetail.bill_schedule.month[-2:]]
            tempList.append(month)
            tempList.append('<a onclick="approval(' + str(scheduleDetail.bill_schedule.id) + ')" >Approve</a>')

            userRoleList.append(tempList)
        data = {'iTotalRecords': total_record, 'iTotalDisplayRecords': total_record, 'aaData': userRoleList}
        # data = {'data': userRoleList}
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|approval.py|approval_list', e
        data = {'msg': 'error'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
@transaction.atomic
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Approve schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def approval_Info(request):
    try:
        get_original = {}
        billScheduleDetails = BillScheduleDetails.objects.get(id=request.GET.get('id'))
        scheduleDetails = BillScheduleDetails.objects.filter(billSchedule=billScheduleDetails.billSchedule,
                                                             is_deleted=False)
        changes_list = []
        for schedule in scheduleDetails.filter().exclude(is_original=True):
            changes_list.append({
                'change_end_date': schedule.end_date.strftime('%d/%m/%Y'),
                'change_accounting_date': schedule.accounting_date.strftime('%d/%m/%Y'),
                'status': schedule.status,

            })

        for schedule in scheduleDetails.filter(is_original=True):
            get_original = {
                'id': request.GET.get('id'),
                'bill_cycle': schedule.billSchedule.bill_cycle.bill_cycle_code,
                'start_date': schedule.start_date.strftime('%d/%m/%Y'),
                'end_date': schedule.end_date.strftime('%d/%m/%Y'),
                'accounting_date': schedule.accounting_date.strftime('%d/%m/%Y'),
                'estimated_date': schedule.estimated_date.strftime('%d/%m/%Y'),
            }
        data = {'success': 'true', 'get_original': get_original, 'changes_list': changes_list}
        return HttpResponse(json.dumps(data), content_type='application/json')

    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|approval.py|approval_Info', e
        data = {'success': 'false', 'error': 'Exception ' + str(e)}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
@transaction.atomic
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Approve schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def approve_changes(request):
    try:
        # pdb.set_trace()
        if request.method == "POST":
            sid = transaction.savepoint()  # Transaction open
            billSchedulesDetails = BillScheduleDetails.objects.get(id=request.POST.get('id'))
            billScheduleObj = billSchedulesDetails.billSchedule
            billSchedulesDetails_old = BillScheduleDetails.objects.get(billSchedule=billScheduleObj,
                                                                       last_confirmed=True)
            billSchedulesDetails_old.last_confirmed = False
            billSchedulesDetails_old.is_original = False
            billSchedulesDetails_old.save()

            billSchedulesDetails.status = 'Confirmed'
            billSchedulesDetails.is_original = True
            billSchedulesDetails.last_confirmed = True
            billSchedulesDetails.save()

            billScheduleApprovalDetails = BillScheduleApprovalDetails.objects.get(bill_schedule=billSchedulesDetails,
                                                                                  status='Pending Approval')
            billScheduleApprovalDetails.status = 'Confirmed'
            billScheduleApprovalDetails.remark = request.POST.get('remark')
            billScheduleApprovalDetails.approval_date = datetime.date.today()
            billScheduleApprovalDetails.save()
            transaction.savepoint_commit(sid)
        data = {'success': 'true'}
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        transaction.rollback(sid)
        print 'Exception|approval.py|approve_changes', e
        data = {'success': 'false', 'message': 'Server Error'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
@transaction.atomic
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Approve schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def reject_changes(request):
    try:
        if request.method == "POST":
            sid = transaction.savepoint()  # Transaction open
            billDetails = BillScheduleDetails.objects.get(id=request.POST.get('id'))
            billDetails.status = 'Rejected'
            billDetails.last_confirmed = False
            billDetails.is_original = False
            billDetails.save()
            billScheduleApprovalDetails = BillScheduleApprovalDetails.objects.get(bill_schedule=billDetails,
                                                                                  status='Pending Approval')
            billScheduleApprovalDetails.status = 'Rejected'
            billScheduleApprovalDetails.remark = request.POST.get('remark')
            billScheduleApprovalDetails.save()
            print 'billScheduleApprovalDetails', billScheduleApprovalDetails
        transaction.savepoint_commit(sid)
        data = {'success': 'true'}
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        transaction.rollback(sid)
        print 'Exception|approval.py|reject_changes', e
        data = {'success': 'false', 'message': 'Server Error'}
        return HttpResponse(json.dumps(data), content_type='application/json')
