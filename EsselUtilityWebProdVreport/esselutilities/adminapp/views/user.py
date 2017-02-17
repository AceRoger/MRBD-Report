import json
from django.http import HttpResponse
from django.shortcuts import render
from adminapp.models import City,UserRole,UserProfile
from django.views.decorators.csrf import csrf_exempt

__author__ = 'vkm chandel'


def open_user_index(request):
    try:
        data={'cities':City.objects.filter(record_status='Active'),
              'roles':UserRole.objects.filter(record_status='Active')
              }
        print 'data',data
    except Exception, e:
        print 'Exception', e
    return render(request, 'adminapp/user_index.html', data)



def list_user(request):
    try:
        print '============================================'
        data = {}
        userList = []
        userProfile = UserProfile.objects.all()
        print 'userProfile',userProfile
        for user in userProfile:
            print user.city_id
            print user.city_id.city_name

            if user.record_status=='Active':
                status='<span style="text-align:center;" class="label label-sm label-success"> Active </span>'
            else:
                status='<span style="text-align:center;" class="label label-sm label-danger"> Inactive </span>'
            edit = '<a class="fa fa-pencil-square fa-lg" onclick=viewUser(' + str(
                user.user_id) + ') ></a> <a title="on/off" class="fa fa-toggle-off" onclick=viewMessage(' + str(user.user_id) + ')  ></a>'
            userList.append({'user': user.user_first_name+' '+user.user_last_name,'role': user.role_id.role_name, 'city': user.city_id.city_name, 'status': status, 'edit': edit})

        data = {'data': userList}
    except Exception, e:
        print 'Exception|user_py|list_user', e
    return HttpResponse(json.dumps(data), content_type='application/json')


def view_user(request):
    try:
        print '======================='
        data = {}
        userProfile = UserProfile.objects.get(user_id=request.GET.get('user_id'))
        data = {'user_id': userProfile.user_id,
                'user_first_name': userProfile.user_first_name,
                'user_last_name': userProfile.user_last_name,
                'user_contact_no': userProfile.user_contact_no,
                'user_email_id': userProfile.user_email_id,
                'city_id': userProfile.city_id.city_name,
                'role_id': userProfile.role_id.role_name,
                'employee_id': userProfile.employee_id,
                'record_status': userProfile.record_status,
                'success': 'true'
                }
        print 'data', data
        print '======================='
    except Exception, e:
        print 'Exception|user_py|view_user', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def save_user(request):
    try:
        print request.POST
        if request.method=="POST":
            userProfile=UserProfile(
                user_first_name=request.POST.get('firstName'),
                user_last_name=request.POST.get('lastName'),
                city_id=City.objects.get(city_id=request.POST.get('userCity')),
                user_email_id=request.POST.get('emailId'),
                role_id=UserRole.objects.get(role_id=request.POST.get('userRole')),
                user_contact_no=request.POST.get('mobileNo'),
                employee_id=request.POST.get('employeeId'),
                user_created_by='Admin'
            )
            userProfile.save()
            data = {'success': 'true'}
        else:
            data = {'success': 'false','error':'Method type is not a POST!'}
    except Exception, e:
        print 'Exception', e
        data = {'success': 'false','error':'Exception '+e}
    return HttpResponse(json.dumps(data), content_type='application/json')