import django
from django.db import models
from django.contrib.auth.models import User
from celery.decorators import task
from django.conf import settings
import traceback
import datetime
from django.views.decorators.csrf import csrf_exempt
from celery.task.schedules import crontab
from celery.decorators import periodic_task
import smtplib
from smtplib import SMTPException
from django.core.urlresolvers import reverse
from scheduleapp.models import BillSchedule, BillScheduleDetails


@periodic_task(run_every=datetime.timedelta(days=1), name="reminder_for_admin", ignore_result=True)
def reminder_for_admin():
    try:
        billScheduleDetails = BillScheduleDetails.objects.filter(is_deleted=False, is_active=True)
        for billSchedule in billScheduleDetails:
            delta = billSchedule.end_date - datetime.date.today()
            if delta.days < 3:
                try:
                    code=billSchedule.billSchedule.bill_cycle.bill_cycle_code
                    month=billSchedule.month
                    date=billSchedule.end_date
                    email = billSchedule.created_by
                    gmail_user ="MUZ_MRBD.Admin@utility.esselgroup.com"
                    gmail_pwd = "alone@2010"
                    FROM =  'Super Admin: <MUZ_MRBD.Admin@utility.esselgroup.com>'
                    TO = [email]
                    SUBJECT = "Immediate attention required: Bill Schedule ending"
                    TEXT = "Dear Essel Admin," "\n\nFollowing bill Cycle need your immediate attention.\n\nBill Cycle Code: "+ code +"\nBill Month: "+ month +"\nEnd Date: "+ date +"\n\nThank you for your attention.\n\nNote: This is system generated email. If not actioned, next reminder will go to Supervior\n\nRegards,\nMRBD Super Admin"
                    server = smtplib.SMTP_SSL()
                    server = smtplib.SMTP("mail.utility.esselgroup.com", 587)
                    server.ehlo()
                    server.starttls()

                    server.login(gmail_user, gmail_pwd)
                    message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
                    server.sendmail(FROM, TO, message)
                    server.quit()
                    data = {'success': 'true'}
                    print 'Request out send_Reminder_Mail with---', TO
                except:
                    pass
            else:
                print None
    except Exception, e:
        print 'Exception ', str(traceback.print_exc())
        print 'Exception|task.py|reminder_for_admin', e
    return
