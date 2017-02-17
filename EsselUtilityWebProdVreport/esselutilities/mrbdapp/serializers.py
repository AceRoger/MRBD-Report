from django.conf import settings
from datetime import datetime
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.auth.models import User
from adminapp.models import UserProfile, BillCycle, RouteDetail, City
from dispatch.models import JobCard, RouteAssignment, MeterReading, MeterStatus, ReaderStatus
from consumerapp.models import ConsumerDetails, UnBilledConsumers
from .models import MeterImage, SuspiciousActivityImage, UserProfileImage


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(max_length=20, required=True)
    imei_no = serializers.CharField(max_length=500, required=True)


class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=50, required=True)
    last_name = serializers.CharField(max_length=50, required=True)
    email = serializers.CharField(max_length=50, required=True)
    contact_no = serializers.CharField(max_length=15, required=True)
    address_line_1 = serializers.CharField(max_length=500, required=True)
    city = serializers.CharField(max_length=500, required=True)

    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'email', 'contact_no', 'address_line_1', 'city')

    def update_profile(self, validated_data, user, userprofileimage=None):
        city_obj = get_object_or_404(City, city=validated_data['city'], is_deleted=False)

        user.first_name = validated_data['first_name']
        user.last_name = validated_data['last_name']
        user.email = validated_data['email']
        user.contact_no = validated_data['contact_no']
        user.address_line_1 = validated_data['address_line_1']
        user.city = city_obj

        try:
            userprofile_obj.image_url = str(settings.MEDIA_URL) + str(userprofileimage.user_profile_image)
        except Exception:
            pass

        user.userprofile.save()
        return user.userprofile


class MeterReadingSerializer(serializers.ModelSerializer):
    #current_meter_reading = serializers.CharField(max_length=20, required=True)
    reading_month = serializers.CharField(max_length=20, required=True)
    job_card_id = serializers.CharField(max_length=20, required=True)

    class Meta:
        model = MeterReading
        #fields = ('job_card_id', 'current_meter_reading', 'reading_month')
        fields = ('job_card_id','reading_month')

    def create(self, validated_data, user):

        print "getting jobcard for : ", validated_data['job_card_id']

        try:
            jobcard_obj = JobCard.objects.get(id=validated_data['job_card_id'])

        except Exception:
            return None

        try:
            meterreading_obj = MeterReading.objects.get(jobcard=jobcard_obj,
                                                        reading_month=validated_data['reading_month'])
            print "Existing Meter reading object found for : ", jobcard_obj.id
            return meterreading_obj  #30012017 by vkm
        except Exception:
            print "creating meter reading"
            try:
                # print validated_data
                meter_status_obj = MeterStatus.objects.get(meter_status=str(validated_data['meter_status']))

                meterreading_obj = MeterReading(jobcard=jobcard_obj, reading_month=validated_data['reading_month'])


                print 'meterreading_obj=====>',meterreading_obj

                print "New meter reading object created"

                if meter_status_obj.meter_status == 'Normal' or meter_status_obj.meter_status == 'ReadingOverflow':
                    if validated_data['current_meter_reading'] is not None or validated_data['current_meter_reading'] != '':
                        meterreading_obj.current_meter_reading = validated_data['current_meter_reading']
                    else:
                        return None
                elif meter_status_obj.meter_status == 'LockPremise' or meter_status_obj.meter_status == 'MeterMissing':
                    meterreading_obj.current_meter_reading = ''
                else:
                    try:
                        meterreading_obj.current_meter_reading = validated_data['current_meter_reading']
                    except Exception:
                        meterreading_obj.current_meter_reading = ''

                print "Meter reading saved"
                try:
                    print str(validated_data['meter_status'])
                    meter_status_obj = MeterStatus.objects.get(meter_status=str(validated_data['meter_status']))
                    meterreading_obj.meter_status = meter_status_obj
                    print "Meter status updated"
                except Exception, e:
                    meter_status_obj = MeterStatus.objects.get(meter_status="Normal")
                    meterreading_obj.meter_status = meter_status_obj
                    print e
                    print "Meter status updated to Normal"

                try:
                    meterreading_obj.reading_taken_by = str(validated_data['reading_taken_by'])
                    print "Meter reading taken by updated"
                except Exception, e:
                    print e
                    meterreading_obj.reading_taken_by = 'Manual'
                    print "Meter reading taken by set to Manual"

                try:
                    print str(validated_data['reader_status'])
                    reader_status_obj = ReaderStatus.objects.get(reader_status=str(validated_data['reader_status']))
                    meterreading_obj.reader_status = reader_status_obj
                    print "Reader status updated"
                except Exception, e:
                    print e
                    reader_status_obj = ReaderStatus.objects.get(reader_status="Normal")
                    meterreading_obj.reader_status = reader_status_obj
                    print "Reader status updated to Normal"

                try:
                    if (str(validated_data['suspicious_activity']) == 'False'):
                        meterreading_obj.suspicious_activity = False
                    else:
                        meterreading_obj.suspicious_activity = True
                except Exception, e:
                    print "Error for SuspiciousActivity", str(e)
                    meterreading_obj.suspicious_activity = False

                try:
                    meterreading_obj.reading_date = datetime.strptime(str(validated_data['reading_date']),
                                                                      '%Y/%m/%d %H:%M:%S');
                except Exception:
                    pass

                try:
                    meterreading_obj.latitude = validated_data['cur_lat']
                except Exception:
                    pass

                try:
                    meterreading_obj.longitude = validated_data['cur_lng']
                except Exception:
                    pass

                try:
                    meterreading_obj.suspicious_activity_remark = validated_data['suspicious_remark']
                except Exception:
                    pass

                try:
                    meterreading_obj.kilowatt = validated_data['kilowatt']
                except Exception:
                    pass

                try:
                    meterreading_obj.consumption = validated_data['consumption']
                except Exception:
                    pass

                try:
                    meterreading_obj.comment = validated_data['reader_remark_comment']
                except Exception:
                    pass

                meterreading_obj.created_by = 'admin'
                meterreading_obj.updated_by = 'admin'

                print "saving meterreader Object"
                meterreading_obj.save()

                if (jobcard_obj.record_status == "REASSIGNED" or jobcard_obj.record_status == "DEASSIGNED"):
                    meterreading_obj.is_deleted = True
                    meterreading_obj.is_active = False
                else:
                    meterreading_obj.is_deleted = False

                jobcard_obj.record_status = "COMPLETED"
                jobcard_obj.is_reading_completed = True
                jobcard_obj.save()

                print "JobCard status updated==>", jobcard_obj

                print "returning meterreader Object : " + str(meterreading_obj.id)
                return meterreading_obj
            except Exception, e:
                print e
                print "error creating meter reading"
                return None


class MeterImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeterImage
        fields = ('meter_image',)


class ConsumerDetailsSerializer(serializers.Serializer):
    consumer_name = serializers.CharField(max_length=200, required=True)
    consumer_no = serializers.CharField(max_length=200, required=True)
    # contact_no = serializers.CharField(max_length=50, required=False)
    bill_cycle_code = serializers.CharField(max_length=100, required=True)
    meter_no = serializers.CharField(max_length=30, required=True)
    reading_month = serializers.CharField(max_length=20, required=False)
    current_meter_reading = serializers.CharField(max_length=20, required=False)

    def create_unbilled_customer(self, validated_data, user):

        unbilledconsumer_obj = UnBilledConsumers(meterreader=user)

        if unbilledconsumer_obj is not None:
            unbilledconsumer_obj.name = validated_data['consumer_name']
            try:
                unbilledconsumer_obj.contact_no = validated_data['contact_no']
            except:
                pass

            unbilledconsumer_obj.consumer_no = validated_data['consumer_no']
            unbilledconsumer_obj.meter_no = validated_data['meter_no']
            unbilledconsumer_obj.bill_cycle_code = validated_data['bill_cycle_code']
            unbilledconsumer_obj.reading_month = validated_data['reading_month']
            unbilledconsumer_obj.current_meter_reading = validated_data['current_meter_reading']

            try:
                unbilledconsumer_obj.reading_date = datetime.strptime(str(validated_data['reading_date']),
                                                                      '%Y/%m/%d %H:%M:%S');
            except Exception:
                pass

            try:
                unbilledconsumer_obj.reading_taken_by = validated_data['reading_taken_by']
            except Exception:
                pass

            try:
                unbilledconsumer_obj.route_code = validated_data['route_code']
            except Exception:
                pass

            try:
                unbilledconsumer_obj.email_id = validated_data['email_id']
            except Exception:
                pass

            try:
                unbilledconsumer_obj.address_line_1 = validated_data['address']
            except Exception:
                pass

            try:
                unbilledconsumer_obj.address_line_2 = validated_data['address_line_2']
            except Exception:
                pass

            try:
                unbilledconsumer_obj.address_line_3 = validated_data['address_line_3']
            except Exception:
                pass

            try:
                unbilledconsumer_obj.pin_code = validated_data['pin_code']
            except Exception:
                pass

            try:
                unbilledconsumer_obj.dtc = validated_data['dtc']
            except Exception:
                pass

            try:
                unbilledconsumer_obj.pole_no = validated_data['pole_no']
            except Exception:
                pass

            try:
                unbilledconsumer_obj.connection_status = validated_data['connection_status']
            except Exception:
                pass

            try:
                unbilledconsumer_obj.meter_status = validated_data['meter_status']
            except Exception:
                pass

            try:
                unbilledconsumer_obj.reader_status = validated_data['reader_status']
            except Exception:
                pass

            try:
                if (str(validated_data['suspicious_activity']) == 'False'):
                    unbilledconsumer_obj.suspicious_activity = False
                else:
                    unbilledconsumer_obj.suspicious_activity = True
            except Exception:
                pass

            try:
                unbilledconsumer_obj.suspicious_activity_remark = validated_data['suspicious_remark']
            except Exception:
                pass

            try:
                unbilledconsumer_obj.comment = validated_data['reader_remark_comment']
            except Exception:
                pass

            try:
                if (str(validated_data['is_qr_tempered']) == 'False'):
                    unbilledconsumer_obj.is_qr_code_tempered = False
                else:
                    unbilledconsumer_obj.is_qr_code_tempered = True
            except Exception:
                pass

            try:
                unbilledconsumer_obj.latitude = validated_data['cur_lat']
            except Exception:
                pass

            try:
                unbilledconsumer_obj.longitude = validated_data['cur_lng']
            except Exception:
                pass

            unbilledconsumer_obj.created_by = 'admin'
            unbilledconsumer_obj.updated_by = 'admin'
            print "Saving Unilled Consumer details"
            unbilledconsumer_obj.save()
            print "Consumer details saved"
            return unbilledconsumer_obj
        return None
