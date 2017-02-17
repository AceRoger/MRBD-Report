import json
import pdb
from time import timezone
import datetime

from adminapp.models import City
from adminapp.models import UserRole
from adminapp.models import UserProfile
# from adminapp.models import Availability
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from authenticateapp.decorator import role_required

#details Of admin render to the card and edit form also
@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def detail_admin(request,admin_id):
    data = {}
    try:
        citys = City.objects.filter(is_deleted=False)
        roles = UserRole.objects.filter(is_deleted=False)

        userPofile_obj = UserProfile.objects.get(id = admin_id)
        name = userPofile_obj.first_name + ' ' + userPofile_obj.last_name
        firstname = userPofile_obj.first_name
        lastname = userPofile_obj.last_name
        employee_id = userPofile_obj.employee_id
        address = userPofile_obj.address_line_1
        email = userPofile_obj.email
        type = userPofile_obj.type
        role = userPofile_obj.role
        city = userPofile_obj.city
        phone = userPofile_obj.contact_no
        status = userPofile_obj.status
        adminid = userPofile_obj.user_ptr_id

        adminData = {'adminid':adminid,'type':type,'city':city,'firstname':firstname,'lastname':lastname,'employee_id':employee_id,'phone':phone,'name': name,'email':email,'status':status,'role':role,'address':address}
        data={'adminData':adminData,'citys':citys,'roles':roles}
    except Exception, e:
        print 'Exception', e
    return render(request,'meterreaderapp/detail_admin.html',data)



# Edit validator models data save into the database
@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def edit_save_admin(request):
    try:

        if request.POST:
            city = City.objects.get(id = request.POST.get('valCity'))

            role = UserRole.objects.get(id=request.POST.get('role'))

            if check_admin_employee_id(request.POST.get('employeeId'), request.POST.get('email')):
                data = {'success': 'exist'}
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                userProfile = UserProfile.objects.get(id=request.POST.get('adminid'))
                userProfile.first_name = request.POST.get('firstName')
                userProfile.last_name = request.POST.get('lastName')
                userProfile.address_line_1 = request.POST.get('address')
                userProfile.contact_no = request.POST.get('contactNo')
                userProfile.city = city
                userProfile.role = role
                userProfile.employee_id = request.POST.get('employeeId')

            if request.POST.get('check_pwdchange_status')=='change_password':
                userProfile.set_password(request.POST.get('password'))

            userProfile.save()
            data = {'success': 'true'}
        else:
               data = {'success': 'false', 'error': 'Method type is  a POST!'}

    except Exception, e:
        print e
        data = {'success': 'false', 'error': 'Exception '}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def check_admin_employee_id(employeeid,email_id):
    try:
        UserProfile.objects.get(Q(employee_id = employeeid),~Q(email=email_id))
        return True
    except UserProfile.DoesNotExist:
        return False
    except Exception, e:
        print 'Exception|detailadmin.py|check_existing_employee_id', e


