import traceback
import json
import pdb
import datetime
import django
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from adminapp.models import UserPrivilege, UserRole,UserProfile
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from authenticateapp.decorator import role_required


__author__ = 'mayur sable'

import logging
log = logging.getLogger(__name__)

@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def open_role_index(request):
    try:
        data = get_roles_privilege()
    except Exception, e:
        print 'Exception|role.py|open_role_index', e
    return render(request, 'adminapp/role_index.html', data)


@csrf_exempt
@transaction.atomic
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def save_user_role(request):
        try:
            sid = transaction.savepoint()  # Transaction open
            data = request.POST
            roleName = request.POST.get('roleName')
            discription = request.POST.get('roleDescription')
            userRole = UserRole(role=str(roleName),
                                description=discription,
                                created_by='Admin')
            userRole.save()
            for key, value in data.iteritems():
                if str(key) != 'roleName' and str(key) != 'roleDescription':
                    userRole.privilege.add(key)
                    userRole.save()
            data = {'success': 'true'}
            transaction.savepoint_commit(sid)
        except Exception, e:
            print 'exception ', str(traceback.print_exc())
            transaction.rollback(sid)
            print 'Exception|role.py|save_user_role', e
            data = {'success': 'false'}
        return HttpResponse(json.dumps(data), content_type='application/json')


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def list_user_role(request):
    try:
        userRoleList = []

        column = request.GET.get('order[0][column]')
        searchTxt = request.GET.get('search[value]')
        order = ""
        if request.GET.get('order[0][dir]') == 'desc':
            order = "-"
        list = ['role']
        column_name = order + list[int(column)]
        start = request.GET.get('start')
        length = int(request.GET.get('length')) + int(request.GET.get('start'))
        total_record = UserRole.objects.filter(Q(status__icontains=searchTxt) | Q(role__icontains=searchTxt),is_deleted=False).count()
        userRole = UserRole.objects.filter(Q(status__icontains=searchTxt) |
                                           Q(role__icontains=searchTxt), is_deleted=False).order_by(column_name)[start:length]
        for role in userRole:
            tempList = []
            if role.status == 'Active':
                status = '<span style="text-align:center;" class="label label-sm label-success"> Active </span>'
                edit1 =  '<a title="Change Status" class="fa fa-toggle-on" style="color: #32c5d2;" onclick="change_status(' + str(
                role.id) + ')" ></a>'
            else:
                status = '<span style="text-align:center;" class="label label-sm label-danger"> Inactive </span>'
                edit1 = '<a title="Change Status" class="fa fa-toggle-on" style="color: #ed1847;" onclick="change_status(' + str(
                role.id) + ')" ></a>'
            edit = '<a title="Edit Role" class="fa fa-pencil" style="color: #ed1847;" onclick="editRole(' + str(
                role.id) + ')" ></a>  <span>|</span> '
            # edit1 =' <input type="checkbox"  data-size="small" class="make-switch" data-on-text="Yes" data-off-text="No" checked>'

            created_date=role.created_date.strftime('%d/%m/%Y')

            userProfile = UserProfile.objects.filter(role=role).first()

            if userProfile:
                associatedUser = UserProfile.objects.filter(role=userProfile.role).count()
            else:
                associatedUser='0'

            tempList.append(role.role)
            tempList.append(role.description)
            tempList.append(created_date)
            tempList.append(associatedUser)
            tempList.append(status)
            tempList.append(edit+edit1)

            userRoleList.append(tempList)
        data = {'iTotalRecords': total_record, 'iTotalDisplayRecords': total_record, 'aaData': userRoleList}
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|role.py|list_user_role', e
        data = {'msg': 'error'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def view_edit_role(request):
    try:
        data = {}
        userRole = UserRole.objects.get(id=request.GET.get('role_id'))
        data = {'userRole': userRole.id,
                'role': userRole.role,
                'description': userRole.description,
                'privileges': [privilege.id for privilege in userRole.privilege.all()],
                'success': 'true'
                }
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|role.py|view_edit_role', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
@transaction.atomic
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def update_user_role(request):
    try:
        # pdb.set_trace()
        data = request.POST
        sid = transaction.savepoint()  # Transaction open
        role_id = request.POST.get('txt_roleId')
        userRole = UserRole.objects.get(id=role_id)
        userRole.role = request.POST.get('editRoleName')
        userRole.description = request.POST.get('editRoleDescription')
        userRole.updated_by = 'Admin'
        userRole.updated_date = datetime.date.today()
        userRole.save()
        userRole.privilege.clear()
        for key, value in data.iteritems():
            if str(key) != 'txt_roleId' and str(key) != 'editRoleName' and str(key) != 'editRoleDescription':
                userRole.privilege.add(key)
                userRole.save()
        transaction.savepoint_commit(sid)
        data = {'success': 'true'}
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        transaction.rollback(sid)
        print 'Exception|role.py|update_user_role', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def record_status_change(request):
    try:
        userRole = UserRole.objects.get(id=request.GET.get('role_id'))
        userProfile = UserProfile.objects.filter(role=userRole).count()
        if userProfile == 0:
            userRole.updated_by = 'Admin'
            userRole.updated_date = datetime.date.today()
            if userRole.status == 'Active':
                userRole.status = 'Inactive'
            else:
                userRole.status = 'Active'
            userRole.save()
            data = {'success': 'true'}
        else:
            data = {'success': 'user'}
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|role.py|record_status_change', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_roles_privilege():
    try:
        data={}
        privileges = UserPrivilege.objects.filter(parent__isnull=True, is_deleted=False)
        privilegesList = []
        for privilege in privileges:
            subPrivileges = UserPrivilege.objects.filter(parent=privilege, is_deleted=False)
            data = {'privilege': privilege, 'subPrivileges': subPrivileges}
            privilegesList.append(data)
            data = {'privileges': privilegesList}
    except Exception, e:
        print 'exception ', str(traceback.print_exc())
        print 'Exception|role.py|get_roles_privilege', e
        data = {'privileges': None}
    return data
