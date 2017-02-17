# Create your views here.
# from django.template import loader, Context
# from django.template.loader import render_to_string
import csv
import json
import pdb
import smtplib
import base64
import MySQLdb, sys
import datetime
import dateutil.relativedelta
from django.shortcuts import render, render_to_response, redirect
# Create your views here
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control
from adminapp.models import *
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.db import transaction

# importing exceptions
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError

from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

# from html5lib import inputstream
# for sending mail
from smtplib import SMTPException
from Crypto.Cipher import AES
#from django.contrib.auth.decorators import  role_required
from decorator import role_required
from urllib import quote, unquote
from adminapp.constraints import SHOW_MONTH
import datetime
from django.db.models import Q
from scheduleapp.models import BillSchedule, PN33Download, BillScheduleDetails, BillScheduleApprovalDetails, UploadB30
from adminapp.models import BillCycle, Utility, City, RouteDetail, UserProfile, UserPrivilege,UserRole
from dispatch.models import MeterStatus, RouteAssignment, JobCard, ReaderStatus, MeterReading, ValidatorAssignment,UnbilledConsumerAssignment

from consumerapp.models import ConsumerDetails, UnBilledConsumers
from django.core.urlresolvers import reverse
from django.contrib.auth import update_session_auth_hash
from django.contrib.messages import get_messages
from django.contrib import messages

Months = {
    1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR',
    5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG',
    9: 'SEPT', 10: 'OCT', 11: 'NOV', 12: 'DEC'}


def checkMonth(month):
    if month > 9:
        return str(month)
    else:
        return '0' + str(month)

#@role_required(roles=['System Admin','Admin','VALIDATOR_1','VALIDATOR_2','Approver','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def index(request):
    if request.user.is_authenticated():
        try:
            if request.user.userprofile.type == "WEB_USER":
                if 'Dashboard' in request.session['privileges'] and 'Import PN33' in request.session['privileges'] and 'Schedule' in request.session[
                    'privileges'] and 'Dispatch' in request.session['privileges'] and 'Upload' in request.session[
                    'privileges'] and 'System User' in request.session['privileges'] and 'Administration' in \
                        request.session['privileges'] and 'Validation1' in request.session[
                    'privileges'] and 'Validation2' in request.session['privileges'] and 'Approve schedule' in \
                        request.session['privileges']:
                    url = reverse('authen:applicationlanding')
                elif 'Dashboard' in request.session['privileges'] and 'Import PN33' in request.session['privileges'] and 'Schedule' in request.session[
                    'privileges'] and 'Dispatch' in request.session['privileges'] and 'Upload' in request.session[
                    'privileges'] and 'System User' in request.session['privileges'] and 'Validation1' in request.session[
                    'privileges'] and 'Validation2' in request.session['privileges']:
                    url = reverse('authen:applicationlanding')
                elif 'Dashboard' in request.session['privileges']:
                    url = reverse('mrbd_dashboard')
                elif 'Import PN33' in request.session['privileges']:
                    url = reverse('consumer:open_pn33_index')
                elif 'Schedule' in request.session['privileges']:
                    url = reverse('schedule:open_bill_schedule')
                elif 'Dispatch' in request.session['privileges']:
                    url = reverse('dispatch:view_jobcard')
                elif 'Upload' in request.session['privileges']:
                    url = reverse('upload:open_upload_index')
                elif 'System User' in request.session['privileges']:
                    url = reverse('meterreader:open-systemuser-index')
                elif 'Administration' in request.session['privileges']:
                    url = reverse('adminapp:open_role_index')
                else:
                    data = {'success': '5', 'message': '5'}
                    return HttpResponse(json.dumps(data), content_type='application/json')



            elif request.user.userprofile.type == "VALIDATOR_1" or request.user.userprofile.type == "VALIDATOR_2":
                url = reverse('validate:validate_jobcard_list')

            elif request.user.userprofile.type == "APPROVAL":
                if 'Approve schedule' in request.session['privileges']:
                    url = reverse('schedule:open-approval-index')
            else:
                data = {'success': '6', 'message': '6'}
                return HttpResponse(json.dumps(data), content_type='application/json')
        except:
            auth_logout(request)
            return redirect('/')

        return HttpResponseRedirect(url)
        #return HttpResponseRedirect(reverse('authen:applicationlanding'))
    return render(request, 'login/index.html')


@csrf_exempt
def login(request):
    #pdb.set_trace()
    url=''
    username = request.POST.get("username")
    password = request.POST.get("password")
    try:
        if request.POST:
            uname = User.objects.get(username=username)
            user = authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    userProfile = UserProfile.objects.get(
                        (Q(type='WEB_USER') | Q(type='VALIDATOR_1') | Q(type='VALIDATOR_2')| Q(type='APPROVAL')), status="ACTIVE", id=user.id)
                    if userProfile.role == None:
                        data = {'success': '5', 'message': '5'}
                        return HttpResponse(json.dumps(data), content_type='application/json')
                    user_type = userProfile.type
                    user_role = userProfile.role.role
                    role_list = []
                    userrole = UserRole.objects.filter(role=userProfile.role)
                    for role in userrole:
                        if role.status == "Inactive":
                            data = {'success': '7', 'message': '7'}
                            return HttpResponse(json.dumps(data), content_type='application/json')
                        role_list.append(str(role.role))
                    request.session['username'] = username

                    privilege_obj = UserPrivilege.objects.filter(
                        userrole=userrole)
                    privilege_list = []
                    for privilege in privilege_obj:
                        privilege_list.append(str(privilege.privilege))
                    request.session['privileges'] = privilege_list

                    if user_type == "WEB_USER" :
                        if 'Dashboard' in request.session['privileges'] and 'Import PN33' in request.session['privileges'] and 'Schedule' in request.session['privileges'] and 'Dispatch' in request.session['privileges'] and 'Upload' in request.session['privileges'] and 'System User' in request.session['privileges'] and 'Administration' in request.session['privileges'] and 'Validation1' in request.session['privileges'] and 'Validation2' in request.session['privileges'] and 'Approve schedule' in request.session['privileges']:
                             url = reverse('authen:applicationlanding')
                        elif 'Dashboard' in request.session['privileges'] and 'Import PN33' in request.session['privileges'] and 'Schedule' in request.session['privileges'] and 'Dispatch' in request.session['privileges'] and 'Upload' in request.session['privileges'] and 'System User' in request.session['privileges'] and 'Validation1' in request.session['privileges'] and 'Validation2' in request.session['privileges']:
                            url = reverse('authen:applicationlanding')
                        elif 'Dashboard' in request.session['privileges']:
                            url = reverse('mrbd_dashboard')
                        elif 'Import PN33' in request.session['privileges']:
                            url = reverse('consumer:open_pn33_index')
                        elif 'Schedule' in request.session['privileges']:
                            url = reverse('schedule:open_bill_schedule')
                        elif 'Dispatch' in request.session['privileges']:
                            url = reverse('dispatch:view_jobcard')
                        elif 'Upload' in request.session['privileges']:
                            url = reverse('upload:open_upload_index')
                        elif 'System User' in request.session['privileges']:
                            url = reverse('meterreader:open-systemuser-index')
                        elif 'Administration' in request.session['privileges']:
                            url = reverse('adminapp:open_role_index')
                        else:
                            data = {'success': '5', 'message': '5'}
                            return HttpResponse(json.dumps(data), content_type='application/json')

                    elif user_type == "VALIDATOR_1" or user_type == "VALIDATOR_2":
                         url = reverse('validate:validate_jobcard_list')

                    elif user_type == "APPROVAL":
                         if 'Approve schedule' in request.session['privileges']:
                             url= reverse('schedule:open-approval-index')
                    else:
                        data = {'success': '6', 'message': '6'}
                        return HttpResponse(json.dumps(data), content_type='application/json')

                    auth_login(request, user)
                    data = {'success': 'true', 'message': 'Login Successfully','url':url}
                    return HttpResponse(json.dumps(data), content_type='application/json')

                else:
                    data = {'success': 'false', 'message': 'User Is Not Active'}
                    return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                data = {'success': 'Invalid Password', 'message': 'Invalid Password'}
                return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception as e:
        print e
        data = {'success': 'false', 'message': 'Invalid Username'}
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception, e:
        print 'Exception|view_py|do_login', e


def welcome(request):
    return render(request, 'login/welcome.html')


def blank(request):
    return render(request, 'login/blank.html')


def users(request):
    if request.user.is_authenticated():
        data = {
            'user_role': User_Role.objects.all().order_by('user_role_name')
        }
    else:
        return render(request, 'login/login.html')


@login_required(login_url='/')
def logout(request):
    if request.user.is_authenticated():
        auth_logout(request)

    return redirect('/')


def forgot_pwd(request):
    return render(request, 'login/forgotpwd.html')


@csrf_exempt
def user_exist(request):
    # pdb.set_trace()
    username = request.POST.get("email")
    try:
        if request.POST:
            user = None
            try:
                user = User.objects.get(username=username)

            except:
                pass
            # emails= UserProfile.objects.filter(user_email_id=request.POST.get("email"))
            # for obj in emails:
            #     user_email_id = obj.user_email_id
            #     User_id= obj.user_id
            if user:
                send_email(request, user.username, user.id)
                data = {'success': 'true', 'message': 'Login Successfully'}
    except Exception as e:
        print e
        data = {'success': 'false', 'message': 'Invalid Username'}
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception, e:
        print 'Exception|view_py|forgot_pwd', e
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def send_email(request, user_email_id, user_id):
    try:
        # pdb.set_trace()
        subject = "Password Reset Link"
        description = request.build_absolute_uri(reverse('authen:reset_pwd'))

        gmail_user = "training.tungsten@gmail.com"
        gmail_pwd = "Essel@2016"
        FROM = ' Admin: <training.tungsten@gmail.com>'
        TO = user_email_id
        plain = str(user_id)
        mismatch = len(plain) % 16
        if mismatch != 0:
            padding = (16 - mismatch) * ' '
            plain += padding
        # msg_text = str(user_id).rjust(32)
        secret_key = '1234567890123456'  # create new & store somewhere safe
        cipher = AES.new(secret_key, AES.MODE_ECB)  # never use ECB in strong systems obviously
        encoded = base64.b64encode(cipher.encrypt(plain))
    except Exception, e:
        print 'exception', e

    try:
        TEXT = "Dear Essel User," "\n \n   You recently requested to reset your password for your Essel account.\n\n please click on below link.\n" + description + '?ID=' + encoded + " " + "\n\nThank You,\nEssel Team"
        SUBJECT = subject
        server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException, e:
        print e
    except Exception, e:
        print 'exception', e

    return 1


@csrf_exempt
def reset_pwd(request):
    secret_key = '1234567890123456'
    email = request.GET.get('ID')
    cipher = AES.new(secret_key, AES.MODE_ECB)
    decoded = cipher.decrypt(base64.b64decode(email))
    data = {'id': decoded}
    return render(request, 'login/resetpwd.html', data)


@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Upload','System User','Administration'],login_url='/',raise_exception=True)
def mrbd_dashboard(request, month=None):
    # pdb.set_trace()
    notStartedpn33 = 0
    startedpn33 = 0
    validationpending=0
    validationcompleted = 0
    notConfirmed = 0
    confirmed = 0
    pendingApproval = 0
    rejected = 0
    failedpn33 = 0
    completedpn33 = 0
    dispending = 0
    uploadedConsumerCount = 0
    pending = 0
    yearMonth = 0
    monthYears = 0
    overallValidated=0
    overallValidatepending=0
    Validated=0
    valpending=0
    unbillConsumer=0
    unbilledConsumerAssignment=0
    validatepending=0
    currentmonth = None
    jobcard=0
    dispatched=0
    validated=0
    # currentmonth = request.POST.get('currentmonth')
    print request.user.userprofile.type

    if month:
        currentmonth = month
    else:
        currentmonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month)
    try:
        monthYears = []
        for month in range(0, SHOW_MONTH):
            date = datetime.date.today() - dateutil.relativedelta.relativedelta(months=month)
            monthYears.append({'value': str(date.year) + checkMonth(date.month),
                               'text': Months[date.month] + ' ' + str(date.year)})

        yearMonth = str(datetime.date.today().year) + checkMonth(datetime.date.today().month)
    except:
        pass
    try:
        billschedule = []
        routeassigneds = []
        billcycles = BillCycle.objects.filter(is_deleted=False)
        for billcycle in billcycles:

            billschedule = BillSchedule.objects.filter(month=currentmonth,is_deleted=False)
            pending = billschedule.filter(is_imported=True,is_uploaded=False,is_deleted=False).count()
            uploadedConsumerCount = billschedule.filter(is_imported=True,is_uploaded=True,is_deleted=False).count()

            if billschedule:
                # for Schedule====================
                billScheduleDetails = BillScheduleDetails.objects.filter(is_deleted=False,month=currentmonth,is_active=True)
                notConfirmed = billScheduleDetails.filter(status='Not Confirmed').count()
                confirmed = billScheduleDetails.filter(status='Confirmed',last_confirmed=True).count()
                pendingApproval = billScheduleDetails.filter(status='Pending Approval').count()
                rejected = billScheduleDetails.filter(status='Rejected').count()
                # for Import====================
                pn33Downloads = PN33Download.objects.filter(is_deleted=False, month=currentmonth)
                notStartedpn33 = pn33Downloads.filter(download_status='Not Started').count()
                startedpn33 = pn33Downloads.filter((Q(download_status='Not Started')|Q(download_status='Started'))).count()
                failedpn33 = pn33Downloads.filter(download_status='Failed').count()
                completedpn33 = pn33Downloads.filter(download_status='Completed').count()
                # for dispatch========================
                try:
                    PN33Downloads=PN33Download.objects.get(bill_schedule__bill_cycle=billcycle,month=currentmonth,download_status='Completed',is_deleted=False)
                    if PN33Downloads:
                        totalroutes = len(RouteDetail.objects.filter(billcycle=billcycle, bill_month=currentmonth))
                        routeassigneds = len(
                            RouteAssignment.objects.filter(routedetail__billcycle=billcycle, reading_month=currentmonth,
                                                           is_active=True))
                        if totalroutes == routeassigneds:
                            dispatched = dispatched + 1
                        else:
                            dispending = dispending + 1
                    else:
                        pass
                except:
                    pass

                # for validation========================
                try:
                    totalconsumer=None
                    meterreading=None
                    totalconsumer = ConsumerDetails.objects.filter(bill_cycle=billcycle, bill_month=currentmonth).count()
                    meterreading = MeterReading.objects.filter(reading_status='complete',reading_month=currentmonth,is_active=True,is_duplicate=False,is_deleted=False).count()
                    if totalconsumer and meterreading:
                        if totalconsumer == meterreading:
                            validated = validated + 1
                        else:
                            valpending = valpending + 1

                except:
                    pass

                #unbilledConsumerAssignment = UnbilledConsumerAssignment.objects.filter(reading_month=currentmonth,is_confirmed=False).count()
                unbillConsumer = UnBilledConsumers.objects.filter(bill_cycle_code=billcycle.bill_cycle_code,reading_month=currentmonth,is_descarded=False,is_confirmed=False).count()
        overallValidated=overallValidated+validated
        overallValidatepending=overallValidatepending+valpending
        data = {
            'NotConfirmed': notConfirmed, 'Confirmed': confirmed,
            'PendingApproval': pendingApproval,
            'Rejected': rejected,
            'overallnotStartedpn33': notStartedpn33,
            'overallStartedpn33': startedpn33, 'overallfailedpn33': failedpn33,
            'overallCompletedpn33': completedpn33, 'notDispatched':dispending,
            'dispatched': dispatched, 'validationpending': overallValidatepending,
            'validationcompleted':overallValidated, 'UnbillConsumer':unbillConsumer,
            'uploaded': uploadedConsumerCount, 'totaluploadpending':pending, 'yearMonth': yearMonth,
            'app': 'mrbd', 'monthYears': monthYears, 'currentmonth': currentmonth,
        }
    except Exception, e:
        print 'Exception|views.py|dashboard', e
        data = {'message': 'Server Error'}
    return render(request, 'dashboard/dashboard.html', data)


def get_dashboard(request):
    try:
        data = render(request, 'dashboard/dashboardBody.html')
    except Exception, e:
        print 'Exception|views.py|get_dashboard', e
        data = {'message': 'Server Error'}
    return HttpResponse(data)


@csrf_exempt
def consumer(request):
    return render(request, 'login/consumer.html')


@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Upload','System User','Administration'],
login_url='/',raise_exception=True)
def applicationlanding(request):
    return render(request, 'dashboard/applicationlanding.html')


@csrf_exempt
def confirm_pwd(request):
    userId = request.POST.get("userid")
    password1 = request.POST.get("password")
    password2 = request.POST.get("confirmpassword")
    try:
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords don't match")
                data = {'success': 'false', 'password2': password2}
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                user = User.objects.get(id=userId)
                user.set_password(password2)
                user.save()
                data = {'success': 'true', 'password': password2}
                return HttpResponse(json.dumps(data), content_type='application/json')

    except Exception as e:
        print e
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
@login_required(login_url='/')
@role_required(privileges=['Dashboard','Import PN33','Schedule','Dispatch','Validation1','Validation2','Approve schedule','Upload','System User','Administration'],login_url='/',raise_exception=True)
def changepassword(request):
    try:
        oldpwd=request.POST.get("oldpw")
        newpwd=request.POST.get("newpwd").strip()
        retypepwd=request.POST.get("retypepwd").strip()
        username = request.user.username
        if not request.user.check_password(request.POST.get("oldpw")):
            data = {'success': 'false', 'message': 'Old password does not match!'}
        elif oldpwd == newpwd:
            data = {'success': 'samepwd', 'message': 'Old Password & new password are same!'}
        elif len(newpwd)< 6 or len(retypepwd)< 6:
            data = {'success': 'blank', 'message': 'Blank space are not allow!'}
        elif newpwd == retypepwd:
            request.user.set_password(newpwd)
            update_session_auth_hash(request, request.user)
            request.user.save()
            data = {'success': 'true', 'message': 'Changed password successfully'}
        else:
            data = {'success': 'false', 'message': 'New password and confirm password does not match!'}
    except Exception, e:
        data = {'success': 'false', 'error': 'Exception ' + str(e)}
        print e

    return HttpResponse(json.dumps(data), content_type='application/json')


    # try:
    #     print ' Old Password =', request.POST.get("oldpw")
    #     print 'New Password=', request.POST.get("newpwd")
    #     print 'retype Password=', request.POST.get("retypepwd")
    #     print 'session name=', request.POST.get("username")
    #
    #     user = authenticate(username=request.POST.get("username"), password=request.POST.get("oldpw"))
    #     print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++', user
    #     if user:
    #         if user.is_active:
    #             pw = request.POST.get("newpwd")
    #             usr = User.objects.get(username=request.POST.get("username"))
    #             usr.set_password(pw)
    #             usr.save()
    #             update_session_auth_hash(request, request.user)
    #             data = {'success': 'true', 'message': 'changed password successfully'}
    #         else:
    #             data = {'success': 'false', 'message': 'Current password are invalid'}
    # except Exception, e:
    #     data = {'success': 'true', 'message': 'invalid'}
    # return HttpResponse(json.dumps(data), content_type='application/json')
