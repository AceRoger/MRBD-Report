import json
import pdb

from adminapp.models import City
from adminapp.models import EmployeeType
from adminapp.models import UserProfile,ApprovalDetails
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from meterreaderapp.models import DeviceDetail
from meterreaderapp.models import PreferredRoutes
from meterreaderapp.models import PreferredBillCycle
from adminapp.models import RouteDetail
from adminapp.models import UserRole
from dispatch.models import MeterReading
from adminapp.models import BillCycle
from django.db.models import Q
from adminapp.constraints import SHOW_MONTH

from adminapp.models import Availability
from dispatch.models import RouteAssignment,ValidatorAssignmentCount,JobCard


from consumerapp.models import ConsumerDetails

from django.contrib.auth.decorators import login_required
import datetime
import csv
import dateutil.relativedelta
from django.db import transaction
from authenticateapp.decorator import role_required


Months = {
    1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR',
    5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG',
    9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'}

@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_user_list(request, month = None):
    data = {}
    final_list = []
    final_list2 = []
    final_list3 = []
    final_list4 = []
    tempList = []
    if month:
        currentmonth = month
    else:
        currentmonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month)

    try:
        monthYears = []
        for month in range(0, SHOW_MONTH):
            date = datetime.date.today() - dateutil.relativedelta.relativedelta(months=month)
            # date = datetime.date.today() - datetime.timedelta(month * 365 / 12)
            monthYears.append({'value': str(date.year) + checkMonth(date.month),
                               'text': Months[date.month] + ' ' + str(date.year)})
        yearMonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month)

        # city shows into the add mr form
        citys = City.objects.filter(is_deleted=False)
        # object      =   datatable name
        roles = UserRole.objects.filter(is_deleted=False)
        routeDetails = RouteDetail.objects.filter(is_deleted=False)
        billCycle = BillCycle.objects.filter(is_deleted=False)


        # userPorfile is  render to job card
        meterReaders = UserProfile.objects.filter(type="METER_READER",is_deleted=False)
        for meterReader in meterReaders:
            name = meterReader.first_name + ' ' + meterReader.last_name
            email = meterReader.email
            employee_id = meterReader.employee_id
            address = meterReader.address_line_1
            phone = meterReader.contact_no
            user_id = meterReader.user_ptr_id
            status = meterReader.status

            # totalRoute=RouteAssignment.objects.filter(meterreader=meterReader,is_reading_completed=False,is_active=True).count()


            data_obj = {'id': user_id, 'address': address, 'employee_id': employee_id, 'phone': phone, 'name': name,
                        'email': email,'status':status,
                       }
            final_list.append(data_obj)

        # Render Validator details on validator page in the form of job card
        validators = UserProfile.objects.filter(Q(type='VALIDATOR_1') | Q(type='VALIDATOR_2'),is_deleted=False)
        for validator in validators:
            name2 = validator.first_name + ' ' + validator.last_name
            email2 = validator.email
            employee_id2 = validator.employee_id
            address2 = validator.address_line_1
            phone2 = validator.contact_no
            user_id2 = validator.user_ptr_id
            status = validator.status
            type = validator.type

            if validator.type == "VALIDATOR_2":
               type='V 2'
            else:
                type = 'V 1'
            data_obj = {'id2': user_id2, 'address2': address2, 'employee_id2': employee_id2, 'phone2': phone2,
                   'name2': name2, 'email2': email2,'status':status,'type':type}

            final_list2.append(data_obj)


        admins = UserProfile.objects.filter(type ="WEB_USER",is_deleted=False)
        for admin in admins:
            name3 = admin.first_name + ' ' + admin.last_name
            email3 = admin.email
            employee_id3 = admin.employee_id
            address3 = admin.address_line_1
            phone3 = admin.contact_no
            user_id3 = admin.user_ptr_id
            status = admin.status
            data_obj={'id3': user_id3, 'address3': address3, 'employee_id3': employee_id3, 'phone3': phone3,
                        'name3': name3, 'email3': email3,'status':status,}
            final_list3.append(data_obj)

        approvals = UserProfile.objects.filter(type ="APPROVAL",is_deleted=False)
        for approval in approvals:
            name = approval.first_name + ' ' + approval.last_name
            email = approval.email
            employee_id = approval.employee_id
            address = approval.address_line_1
            phone = approval.contact_no
            user_id = approval.user_ptr_id
            status = approval.status
            approdays = ApprovalDetails.objects.get(approval=approval,is_deleted=False)
            days = approdays.days

            data_obj={'id3': user_id, 'address': address,'employee_id': employee_id, 'phone': phone,
                        'name': name, 'email': email,'status':status,'days':days}
            final_list4.append(data_obj)
        data = {'loggedinuser': request.user.userprofile,'monthYears':monthYears,'yearMonth':yearMonth,'final_list4':final_list4,'final_list3': final_list3,'final_list2': final_list2, 'final_list': final_list,'citys': citys,'currentmonth':currentmonth,
                'routeDetails': routeDetails, 'billCycle': billCycle,'roles': roles,}
    except Exception, e:
        print 'Exception', e
    return render(request, 'meterreaderapp/systemuser_index.html', data)


def checkMonth(month):
    if month > 9:
        return str(month)
    else:
        return '0' + str(month)


# Render Edited data on approval edit page
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def view_edit_approval(request):
    try:
        # pdb.set_trace()
        data = []
        data1 = {}
        data2 = {}
        userProfile = UserProfile.objects.get(id=request.GET.get('app_id'))
        data1 = {
                'Fname': userProfile.first_name,
                'Lname': userProfile.last_name,
                'ApprovemailID': userProfile.email,
                'phone':userProfile.contact_no,
                # 'days':ApprovalDetails.days,
                'success': 'true'
                }
        approvDetails = ApprovalDetails.objects.get(approval=request.GET.get('app_id'))
        data2 ={
            'days':approvDetails.days
        }
        data = {'success': 'true','data1':data1,'data2':data2}
        print "data",data
    except Exception, e:
        print 'Exception|systemuser.py|view_edit_approval', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def get_route(request):
    bill_cycle_code = request.POST.get('bill_cycle_code')
    route_list = []
    try:
        billcycle = BillCycle.objects.get(id=bill_cycle_code)
        route_objs=RouteDetail.objects.filter(billcycle=billcycle).order_by('route_code').values('route_code').distinct()
        for route in route_objs:
            options_data = '<option value=' + route['route_code'] + '>' + route['route_code'] + '</option>'
            route_list.append(options_data)
        data = {'route_list': route_list}

    except Exception, e:
        print e
        data = {'route_list': 'none', 'message': 'No city available'}
    return HttpResponse(json.dumps(data), content_type='application/json')


# Activate-Deactivate User Toggle Switch
from django.db.models import Sum

@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def change_user_status(request):

    print request.POST.get('status')#return true=Active,false=Inactive
    user=request.POST.get('user_id')
    try:
        userObj = UserProfile.objects.get(user_ptr_id=request.POST.get('user_id'))

        status=request.POST.get('status')
        if status=='true':
            userObj.status = 'ACTIVE'
            data = {'success': 'true','user_id':userObj.id}
        else:
            if userObj.type=='VALIDATOR_1' or userObj.type=='VALIDATOR_2':
                a=ValidatorAssignmentCount.objects.filter(user=user)

                valcount=ValidatorAssignmentCount.objects.filter(user=user).aggregate(Sum('count'))
                if valcount['count__sum'] is None or valcount['count__sum']<=0:
                    userObj.status = 'INACTIVE'
                    data = {'success': 'true','user_id':userObj.id}
                else:
                    data = {'success': 'assigned','user_id':userObj.id}

            elif userObj.type=='METER_READER':
                b=RouteAssignment.objects.filter(meterreader_id=user)

                routeAssignment = RouteAssignment.objects.filter(meterreader_id=user,is_active=True,is_reading_completed=False).count()
                revisit = JobCard.objects.filter(meterreader=user, is_active=True, is_deleted=False,
                                                 is_reading_completed=False, is_revisit=True).count()

                print (routeAssignment<=0 and revisit <= 0)

                if routeAssignment<=0 and revisit <= 0:
                    userObj.status = 'INACTIVE'
                    data = {'success': 'true','user_id':userObj.id}
                else:
                    data = {'success': 'assigned','user_id':userObj.id}
            else:
                userObj.status = 'INACTIVE'
                data = {'success': 'true','user_id':userObj.id}

        userObj.save()

    except Exception, e:
        print e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')



# save meterraeder details into the database
@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
@transaction.atomic
def save_mr(request):

    try:
        print 'request in with---',request.POST
        sid = transaction.savepoint()  # Transaction open
        password = request.POST.get('password').strip();
        repassword = request.POST.get('retypePassword').strip();
        if password != repassword:
            raise Exception('Password Does Not Match');
        if request.method == "POST":

            if check_existing_employee_id(request.POST.get('employeeId')):
                data = {'success': 'mridexist'}
                return HttpResponse(json.dumps(data), content_type='application/json')


            if check_existing_mr_email_id(request.POST.get('emailID')):
                data = {'success': 'mremailexist'}
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                userProfile = UserProfile(
                         first_name=request.POST.get('firstName'),
                         last_name=request.POST.get('lastName'),
                         username=request.POST.get('emailID'),
                         type='METER_READER',
                         email=request.POST.get('emailID'),
                         address_line_1=request.POST.get('address'),
                         contact_no=request.POST.get('contactNo'),
                         employee_id=request.POST.get('employeeId'),
                         city=City.objects.get(id=request.POST.get('mrCity'))

                )
            userProfile.set_password(password)
            userProfile.is_active = True
            userProfile.save()

            deviceDetail = DeviceDetail(
                company_name=request.POST.get('companyName'),
                device_name=request.POST.get('deviceId'),
                make=request.POST.get('mrMake'),
                imei_no=request.POST.get('mrIMEI'),
                user_id=userProfile
            )
            deviceDetail.save()

            PreferredRoutes(bill_cycle_code=BillCycle.objects.get(id=request.POST.get('billCycleOne')),route=request.POST.get('routeDetailOne'), user=userProfile,preference_no='1').save()
            PreferredRoutes(bill_cycle_code=BillCycle.objects.get(id=request.POST.get('billCycleTwo')),route=request.POST.get('routeDetailTwo'), user=userProfile, preference_no='2').save()
            PreferredRoutes(bill_cycle_code=BillCycle.objects.get(id=request.POST.get('billCycleThree')),route=request.POST.get('routeDetailThree'), user=userProfile, preference_no='3').save()
            PreferredRoutes(bill_cycle_code=BillCycle.objects.get(id=request.POST.get('billCycleFour')),route=request.POST.get('routeDetailFour'), user=userProfile, preference_no='4').save()

            availability_obj = Availability(
                available="AVAILABLE",
                validator=UserProfile.objects.get(id=userProfile.id)
            )
            availability_obj.save()
            transaction.savepoint_commit(sid)
            print 'availability_obj', availability_obj
            data = {'success': 'true'}
        else:
            data = {'success': 'false', 'error': 'Method type is not a POST!'}

        print 'request out with---',data
    except Exception, e:

        transaction.rollback(sid)
        print e
        data = {'success': 'false', 'error': 'Exception '}
    return HttpResponse(json.dumps(data), content_type='application/json')



# check condition for Employee Id is Unique
@csrf_exempt
def check_existing_employee_id(employeeid):
    try:
        UserProfile.objects.get(employee_id = employeeid)
        return True
    except UserProfile.DoesNotExist:
        return False
    except Exception, e:
        print 'Exception|systemuser.py|check_existing_employee_id', e

# check condition for unique email id
@csrf_exempt
def check_existing_mr_email_id(emailid):
    try:
        UserProfile.objects.get(email=emailid)
        return True
    except UserProfile.DoesNotExist:
        return False
    except Exception, e:
        print 'Exception|systemuser.py|check_existing_mr_email_id', e



# Save Validator Details when we create first Time
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
@csrf_exempt
def save_validtor(request):
    try:

        sid = transaction.savepoint()

        password = request.POST.get('valPassword');
        repassword = request.POST.get('valretypePassword');
        if password != repassword:
            raise Exception('Password Does Not Match');
        if request.method == "POST":

            if check_existing_validator_id(request.POST.get('employeeId')):
               data = {'success': 'idexist'}
               return HttpResponse(json.dumps(data), content_type='application/json')


            if check_existing_email_id(request.POST.get('emailID')):
                 data = {'success': 'emailexist'}
                 return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                 userProfile = UserProfile(
                        first_name=request.POST.get('firstName'),
                        last_name=request.POST.get('lastName'),
                        username=request.POST.get('emailID'),
                        email=request.POST.get('emailID'),
                        address_line_1=request.POST.get('address'),

                        type=request.POST.get('validator'),
                        role=UserRole.objects.get(role=request.POST.get('validator')),

                        contact_no=request.POST.get('contactNo'),
                        employee_id=request.POST.get('employeeId'),
                        city=City.objects.get(id=request.POST.get('mrCity')),
                        # role = UserRole.objects.get(id=request.POST.get('validator'))
                 )
            userProfile.set_password(password)
            userProfile.is_active = True
            userProfile.save()


            availability_obj = Availability(
                available="AVAILABLE",
                validator=UserProfile.objects.get(id=userProfile.id)
            )
            availability_obj.save()

            PreferredBillCycle(bill_cycle_code=request.POST.get('prefBillCycleOne'), user=userProfile,preference_no='1').save()
            PreferredBillCycle(bill_cycle_code=request.POST.get('prefBillCycleTwo'), user=userProfile,preference_no='2').save()

            data = {'success': 'true'}
        else:
            data = {'success': 'false', 'error': 'Method type is not a POST!'}

    except Exception, e:
        transaction.rollback(sid)
        print 'Exception', e
        data = {'success': 'false', 'error': 'Exception '}
    return HttpResponse(json.dumps(data), content_type='application/json')


# check condition for Employee Id is Unique
@csrf_exempt
def check_existing_validator_id(employeeid):
    try:
        UserProfile.objects.get(employee_id = employeeid)
        return True
    except UserProfile.DoesNotExist:
        return False
    except Exception, e:
        print 'Exception|systemuser.py|check_existing_validator_id', e


# check condition for unique email id
@csrf_exempt
def check_existing_email_id(emailid):
    try:
        UserProfile.objects.get(email=emailid)
        return True
    except UserProfile.DoesNotExist:
        return False
    except Exception, e:
        print 'Exception|systemuser.py|check_existing_email_id', e


# Edit models data save into the database of meterreader
@csrf_exempt
@transaction.atomic
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Approve schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def edit_save_approver(request):
    try:
        sid = transaction.savepoint()
        userProfile = UserProfile.objects.get(email=request.POST.get('ApprovemailID'))

        userProfile.first_name = request.POST.get('Fname')
        userProfile.last_name = request.POST.get('Lname')
        if request.POST.get('check_pwdchange_status') == 'change_password':
            userProfile.set_password(request.POST.get('Approvpassword'))
        userProfile.save()
        transaction.savepoint_commit(sid)
        data = {'success': 'true'}
    except Exception, e:
        print 'Exception|systemuser.py|edit_save_approver', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')



#  check condition for unique email id
# @csrf_exempt
# def check_employee_id(emailid):
#     try:
#         UserProfile.objects.get(email=emailid)
#         return True
#     except UserProfile.DoesNotExist:
#         return False
#     except Exception, e:
#         print 'Exception|systemuser.py|check_existing_email_id', e



@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def save_admin(request):
    try:
        sid = transaction.savepoint()
        password = request.POST.get('adminPassword');
        repassword = request.POST.get('adminretypePassword');
        if password != repassword:
            raise Exception('Password Does Not Match');
        if request.method == "POST":
            # print 'check_existing_admin_id(request.POST.get('')',check_existing_admin_id(request.POST.get('employeeId'))
            if check_existing_admin_id(request.POST.get('employeeId')):
                data = {'success': 'adminidexist'}
                return HttpResponse(json.dumps(data), content_type='application/json')


            if check_existing_email_id(request.POST.get('emailID')):
                data = {'success': 'adminemailexist'}
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                userProfile = UserProfile(
                    first_name=request.POST.get('firstName'),
                    last_name=request.POST.get('lastName'),
                    username=request.POST.get('emailID'),
                    email=request.POST.get('emailID'),
                    address_line_1=request.POST.get('address'),
                    # type=request.POST.get('validator'),
                    contact_no=request.POST.get('contactNo'),
                    employee_id=request.POST.get('employeeId'),
                    role = UserRole.objects.get(id=request.POST.get('role')),
                    city=City.objects.get(id=request.POST.get('mrCity'))
                )
                userProfile.set_password(password)
                userProfile.is_active = True
                userProfile.save()
                data = {'success': 'true'}
        else:
            data = {'success': 'false', 'error': 'Method type is not a POST!'}

    except Exception, e:
        print 'Exception', e
        data = {'success': 'false', 'error': 'Exception '}
    return HttpResponse(json.dumps(data), content_type='application/json')

# check condition for Employee Id is Unique
@csrf_exempt
def check_existing_admin_id(employeeid):
    try:
        UserProfile.objects.get(employee_id = employeeid)
        return True
    except UserProfile.DoesNotExist:
        return False
    except Exception, e:
        print 'Exception|systemuser.py|check_existing_validator_id', e


@csrf_exempt
def check_existing_admin_email_id(emailid):
    try:
        UserProfile.objects.get(email=emailid)
        return True
    except UserProfile.DoesNotExist:
        return False
    except Exception, e:
        print 'Exception|systemuser.py|check_existing_email_id', e


@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def reading_export_systemuser(request):

    fromDate=datetime.datetime.strptime(request.GET.get('fromdate'), '%d/%m/%Y')
    toDate=datetime.datetime.strptime(request.GET.get('todate'), '%d/%m/%Y')
    toDate= toDate + datetime.timedelta(days=1)
    # datetime.now() + timedelta(days=1)
    print "toDate",toDate
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="readings_mr.csv"';
        writer = csv.writer(response)
        writer.writerow(
            ['BILL_CYC','ROUTE_CODE','BILL_MONTH','CONSUMER_NO','CONSUMER_NAME','METER_READER_NAME','METER_NO',
             'CURRENT_MT_READING','METER_STS','READER_STS','REMARK','READING_DATE','RD_TAKEN_BY',])


        meterReadings = MeterReading.objects.filter(reading_date__gte=fromDate,reading_date__lte =toDate, is_active=True,
                                    is_duplicate=False, is_deleted=False)
        for meterReading in meterReadings:
            tempList = []

            consumerDetail = ConsumerDetails.objects.get(id=meterReading.jobcard.consumerdetail.id)

            tempList.append(consumerDetail.bill_cycle.bill_cycle_code)
            tempList.append(consumerDetail.route.route_code)
            tempList.append(meterReading.reading_month)
            tempList.append(consumerDetail.consumer_no)
            tempList.append(consumerDetail.name)
            tempList.append(meterReading.jobcard.meterreader.first_name + '  ' + meterReading.jobcard.meterreader.last_name)
            tempList.append(consumerDetail.meter_no)
            tempList.append(meterReading.current_meter_reading)
            tempList.append(meterReading.meter_status)
            tempList.append(meterReading.reader_status)
            tempList.append(meterReading.comment)
            tempList.append(meterReading.reading_date.strftime('%d-%m-%Y'))
            tempList.append(meterReading.reading_taken_by)
            writer.writerow(tempList)

        data = {'message': 'Server Success'}
        return response
    except Exception, e:
        print 'Exception|systemuser.py|reading_export_systemuser', e
        data = {'message': 'Server Error'}
    return HttpResponse(json.dumps(data), content_type='application/json')



@csrf_exempt
def refresh(request):
  current_month = request.POST.get('current_month')
  jobcardcount=0
  count=0
  try:

      routeassignmentobjs=RouteAssignment.objects.filter(is_deleted = False,reading_month=current_month)
      for routeassignmentobj in routeassignmentobjs:
        try:
          count=count +1
          jobcards=JobCard.objects.filter(~Q(meterreader=None),routeassigned=routeassignmentobj,is_active=True,is_deleted=False,is_reading_completed=True,reading_month=current_month)
          if jobcards:
            jobcardcount=len(jobcards)
            totalConsumer = ConsumerDetails.objects.filter(route=routeassignmentobj.routedetail, bill_month = current_month,is_deleted=False)
            totalconsumer=len(totalConsumer)
            if jobcardcount==totalconsumer:
              routeassignmentobj.is_reading_completed=True
              routeassignmentobj.save()
            else:
              routeassignmentobj.is_reading_completed=False
              routeassignmentobj.save()
        except:
          pass

      data = {'success':'success'}
  except:
    pass
    data = {'success':'success'}
  return HttpResponse(json.dumps(data), content_type='application/json')

