import django
import json
import base64
from django.db import models
from django.contrib.auth.models import User
from celery.decorators import task
from django.conf import settings
import traceback
import datetime
from django.core.files.uploadedfile import SimpleUploadedFile
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from adminapp.models import RouteDetail,UserProfile
from dispatch.models import RouteAssignment,JobCard, RouteDeassigned, ValidatorAssignmentCount, ValidatorAssignment, MeterReading
from scheduleapp.models import BillSchedule,BillScheduleDetails
from consumerapp.models import ConsumerDetails, UnBilledConsumers
from .models import MeterImage, SuspiciousActivityImage, UserProfileImage, QrTemperedImage
from django.db.models import Q

@task(name="aysnc-update-jc-status")
def aysnc_update_jc_status(jc_array):
    try:
        print "Updating Job Cards"

        route_assigned = []

        for jc_id in jc_array:
            jc = JobCard.objects.get(id=jc_id)
            jc.record_status = 'ASSIGNED'

            if jc.routeassigned is not None:
                if jc.routeassigned in route_assigned:
                    pass
                else:
                    route_assigned.append(jc.routeassigned)
            jc.save()
        if len(route_assigned) > 0:
            for route_assignedOne in route_assigned:
                if route_assignedOne is not None:
                    route_assignedOne.sent_to_mr = True
                    route_assignedOne.dispatch_status = 'Dispatched'
                    route_assignedOne.save()

        print "Job Cards Updated"
    except Exception, e:
    	print "Error updating jc status ",e
    return

@task(name="aysnc-update-rd-jc-status")
def aysnc_update_rd_jc_status(jc_array):
    try:
        print "Updating RD Job Cards"

        route_assigned = None

        for jc_id in jc_array:
            jc = JobCard.objects.get(id=jc_id)
            jc.is_deleted_for_mr = True

            if route_assigned is None:
                route_assigned = jc.routeassigned

            jc.save()

        # if route_assigned is not None:
        #     route_assigned.sent_to_mr = True
        #     route_assigned.dispatch_status = 'Dispatched'
        #     route_assigned.save()

        print "RD Job Cards Updated"
    except Exception, e:
        print "Error updating rd jc status ",e
    return

@task(name="aysnc-create-image-for-upload")
def aysnc_create_image_for_upload(imagedata_dict):
    print "Started uploading in Celery for Meter Reading uplod"

    for key in imagedata_dict:
        print "Creating meter image for JobCard : ",str(key)
        meter_image = json.loads(imagedata_dict[key]['meter_image'])

        try:
            suspicious_activity_image = json.loads(imagedata_dict[key]['suspicious_activity_image'])
        except Exception:
            suspicious_activity_image = None

        try:
            qr_tempered_image = json.loads(imagedata_dict[key]['qr_tempered_image'])
        except Exception:
            qr_tempered_image = None

        print "Fetching meter reading object for JobCard : ",str(key)
        try:
            meterreading_obj = MeterReading.objects.get(id=int(key))
            print "Meter reading object found for JobCard : ",str(key)

            print "Creating Meter image for JobCard: ",str(key)

            meter_image_file = get_image_file(str(meter_image["image"]))

            meter_image_obj = MeterImage(meter_image=SimpleUploadedFile(
                meter_image["name"],
                meter_image_file,
                getattr(meter_image,"content_type","application/octet-stream")))

            meter_image_obj.save()

            print "Meter image created for JobCard: ",str(key)

            meterreading_obj.image_url = str(settings.MEDIA_URL)+str(meter_image_obj.meter_image)
            meterreading_obj.save()
            try:
                if suspicious_activity_image is not None:
                    print "Creating Suspicious Activity Image for JobCard: ",str(key)
                    suspicious_activity_image_file = get_image_file(str(suspicious_activity_image["image"]))

                    suspicious_activity_image_obj = SuspiciousActivityImage(suspicious_activity_image=SimpleUploadedFile(
                        suspicious_activity_image["name"],
                        suspicious_activity_image_file,
                        getattr(suspicious_activity_image,"content_type","application/octet-stream")))

                    suspicious_activity_image_obj.save()

                    meterreading_obj.suspicious_image_url = str(settings.MEDIA_URL)+str(suspicious_activity_image_obj.suspicious_activity_image)
                    meterreading_obj.save()
                    print "Suspicious Activity Image created for JobCard: ",str(key)
                else:
                    print "Suspicious Activity Image not found for JobCard: ",str(key)
                    pass
            except:
                pass

            if qr_tempered_image is not None:
                print "Creating Qr Tempered Image for JobCard: ",str(key)

                qr_tempered_image_file = get_image_file(str(qr_tempered_image["image"]))

                qr_tempered_image_obj = QrTemperedImage(qr_tempered_image=SimpleUploadedFile(
                    qr_tempered_image["name"],
                    qr_tempered_image_file,
                    getattr(qr_tempered_image,"content_type","application/octet-stream")))

                qr_tempered_image_obj.save()

                meterreading_obj.qr_code_image_url = str(settings.MEDIA_URL)+str(qr_tempered_image_obj.qr_tempered_image)
                print "Qr Tempered Image created for JobCard: ",str(key)
            else:
                print "Qr Tempered Image not found for JobCard: ",str(key)
                pass

            print "Saving Meter reading object for JobCard: ",str(key)
            meterreading_obj.save()
            print "Meter reading object saved for JobCard: ",str(key)
        except Exception,e:
            print "Error fetching meter reading object for JobCard : ",str(key)
    print "Uploading completed in Celery for Meter Reading uplod"
    return

@task(name="aysnc-create-image-for-unbilled")
def aysnc_create_image_for_unbilled(imagedata_dict):

    print "Started uploading in Celery"

    for key in imagedata_dict:
        meter_image = json.loads(imagedata_dict[key]['meter_image'])

        try:
            suspicious_activity_image = json.loads(imagedata_dict[key]['suspicious_activity_image'])
        except Exception:
            suspicious_activity_image = None

        try:
            qr_tempered_image = json.loads(imagedata_dict[key]['qr_tempered_image'])
        except Exception:
            qr_tempered_image = None

        unbilledconsumer_obj = UnBilledConsumers.objects.get(id=int(key))

        meter_image_file = get_image_file(str(meter_image["image"]))

        meter_image_obj = MeterImage(meter_image=SimpleUploadedFile(
            meter_image["name"],
            meter_image_file,
            getattr(meter_image,"content_type","application/octet-stream")))

        meter_image_obj.save()

        unbilledconsumer_obj.image_url = str(settings.MEDIA_URL)+str(meter_image_obj.meter_image)
        unbilledconsumer_obj.save()

        if suspicious_activity_image is not None:
            print "Creating Suspicious Activity Image for JobCard: ",str(key)
            suspicious_activity_image_file = get_image_file(str(suspicious_activity_image["image"]))

            suspicious_activity_image_obj = SuspiciousActivityImage(suspicious_activity_image=SimpleUploadedFile(
                suspicious_activity_image["name"],
                suspicious_activity_image_file,
                getattr(suspicious_activity_image,"content_type","application/octet-stream")))

            suspicious_activity_image_obj.save()

            unbilledconsumer_obj.suspicious_image_url = str(settings.MEDIA_URL)+str(suspicious_activity_image_obj.suspicious_activity_image)
            unbilledconsumer_obj.save()

            print "Suspicious Activity Image created for JobCard: ",str(key)
        else:
            print "Suspicious Activity Image not found for JobCard: ",str(key)
            pass

        if qr_tempered_image is not None:
            print "Creating Qr Tempered Image for JobCard: ",str(key)

            qr_tempered_image_file = get_image_file(str(qr_tempered_image["image"]))

            qr_tempered_image_obj = QrTemperedImage(qr_tempered_image=SimpleUploadedFile(
                qr_tempered_image["name"],
                qr_tempered_image_file,
                getattr(qr_tempered_image,"content_type","application/octet-stream")))

            qr_tempered_image_obj.save()

            unbilledconsumer_obj.qr_code_image_url = str(settings.MEDIA_URL)+str(qr_tempered_image_obj.qr_tempered_image)
            print "Qr Tempered Image created for JobCard: ",str(key)
        else:
            print "Qr Tempered Image not found for JobCard: ",str(key)
            pass

        unbilledconsumer_obj.save()
    return

def get_image_file(imagestring):

    image_data = str(imagestring)

    missing_padding = len(image_data) % 4

    if missing_padding != 0:
        image_data += b'='* (4 - missing_padding)

    return base64.b64decode(image_data)
