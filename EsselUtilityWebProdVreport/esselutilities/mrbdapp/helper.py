from django.conf import settings
from django.core import serializers
from django.shortcuts import render,get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.authtoken.models import Token
from adminapp.models import UserProfile
from dispatch.models import JobCard,MeterReading
from consumerapp.models import ConsumerDetails
from scheduleapp.models import BillSchedule, BillScheduleDetails
from meterreaderapp.models import DeviceDetail

def UserProfileToJSON(userprofileObj,devicedetailObj):
	dict = {}
	attributes = []
	dict1 = {}

	dict1["meter_reader_id"] = str(userprofileObj.id)
	dict1["meter_reader_name"] = str(userprofileObj.first_name) + ' ' + str(userprofileObj.last_name)
	dict1["address"] = str(userprofileObj.address_line_1) + " " + str(userprofileObj.address_line_2)
	dict1["contact_no"] = str(userprofileObj.contact_no)

	dict1["email_id"] = str(userprofileObj.email)
	dict1["emp_id"] = str(userprofileObj.employee_id)

	try:
		dict1["city"] = str(userprofileObj.city.city)
	except Exception:
		pass

	try:
		dict1["state"] = str(userprofileObj.state.state)
	except Exception:
		pass

	try:
		dict1["emp_type"] = str(userprofileObj.employee_type.employee_type)
	except Exception:
		pass
	
	try:
		dict1["role"] = str(userprofileObj.role.role)
	except Exception:
		pass
	
	dict1["status"] = str(userprofileObj.status)
	dict1["device_make"] = str(devicedetailObj.make)
	dict1["device_imei_id"] = str(devicedetailObj.imei_no)

	attributes.append(dict1)
	dict['user_info'] = attributes
	return dict



def JobCardToJSON(jobcardObj):
	try:
		consumer = get_object_or_404(ConsumerDetails,id=jobcardObj.consumerdetail_id)
		print "Consumer details found for : ", str(jobcardObj.id)

		bill_schedule = get_object_or_404(BillSchedule,bill_cycle=consumer.bill_cycle,month=consumer.bill_month)
		print "Bill Schedule found for : ", str(jobcardObj.id)

		bill_schedule_details = get_object_or_404(BillScheduleDetails,billSchedule=bill_schedule,last_confirmed=True)
		print "Bill Schedule details found for : ", str(jobcardObj.id)

		dict = {}
		if consumer is not None:
			try:
				dict["consumer_no"] = str(consumer.consumer_no)
			except Exception:
				dict["consumer_no"] = " "

			dict["consumer_id"] = str(consumer.id)
			dict["consumer_name"] = str((consumer.name).encode('utf-8'))
			dict["address"] = str((consumer.address_line_1).encode('utf-8')) + " " + str((consumer.address_line_2).encode('utf-8')) + " " + str((consumer.address_line_3).encode('utf-8'))
			dict["phone_no"] = str((consumer.contact_no).encode('utf-8'))

			dict["route_code"] = str(consumer.route.route_code)
			dict["bill_cycle_code"] = str(consumer.bill_cycle.bill_cycle_code)
			dict["dt_code"] = str(consumer.dtc)
			dict["pole_no"] = str(consumer.pole_no)
			dict["prv_meter_reading"] = str(consumer.prev_reading)

			dict["schedule_month"] = str(bill_schedule_details.month)
			dict["schedule_start_date"] = str(bill_schedule_details.start_date)
			dict["schedule_end_date"] = str(bill_schedule_details.end_date)
			dict["schedule_accounting_date"] = str(bill_schedule_details.accounting_date)
			dict["schedule_estimated_date"] = str(bill_schedule_details.estimated_date)
			dict["meter_reader_id"] = str(jobcardObj.meterreader.id)
			dict["meter_no"] = str((consumer.meter_no).encode('utf-8'))
			dict["is_revisit"] = str(jobcardObj.is_revisit)
			dict["assigned_date"] = str(jobcardObj.assigned_date)
			dict["completion_date"] = str(jobcardObj.completion_date)
			dict["job_card_status"] = str(jobcardObj.record_status)
			dict["job_card_id"] = str(jobcardObj.id)
			print '=======================operation complete==========================='
		return dict
	except Exception,e:
		print 'Exception|JobCardToJSON| ',e
		return dict



def JobCardToJSON__01(jobcardObj):
	
	consumer = get_object_or_404(ConsumerDetails,id=jobcardObj.consumerdetail_id)
	print "Consumer details found for : ", str(jobcardObj.id)

	bill_schedule = get_object_or_404(BillSchedule,bill_cycle=consumer.bill_cycle,month=consumer.bill_month)
	print "Bill Schedule found for : ", str(jobcardObj.id)

	bill_schedule_details = get_object_or_404(BillScheduleDetails,billSchedule=bill_schedule,last_confirmed=True)
	print "Bill Schedule details found for : ", str(jobcardObj.id)

	dict = {}
	if consumer is not None:
		
		try:
			dict["consumer_no"] = str(consumer.consumer_no)
		except Exception:
			dict["consumer_no"] = " "
		
		dict["consumer_id"] = str(consumer.id)
		dict["consumer_name"] = str(consumer.name)
		dict["address"] = str(consumer.address_line_1) + " " + str(consumer.address_line_2) + " " + str(consumer.address_line_3)
		dict["phone_no"] = str(consumer.contact_no)

		dict["route_code"] = str(consumer.route.route_code)
		dict["bill_cycle_code"] = str(consumer.bill_cycle.bill_cycle_code)
		dict["dt_code"] = str(consumer.dtc)
		dict["pole_no"] = str(consumer.pole_no)
		dict["prv_meter_reading"] = str(consumer.prev_reading)

		dict["schedule_month"] = str(bill_schedule_details.month)
		dict["schedule_start_date"] = str(bill_schedule_details.start_date)
		dict["schedule_end_date"] = str(bill_schedule_details.end_date)
		dict["schedule_accounting_date"] = str(bill_schedule_details.accounting_date)
		dict["schedule_estimated_date"] = str(bill_schedule_details.estimated_date)
		dict["meter_reader_id"] = str(jobcardObj.meterreader.id)
		dict["meter_no"] = str(consumer.meter_no)
		dict["is_revisit"] = str(jobcardObj.is_revisit)
		dict["assigned_date"] = str(jobcardObj.assigned_date)
		dict["completion_date"] = str(jobcardObj.completion_date)
		dict["job_card_status"] = str(jobcardObj.record_status)
		dict["job_card_id"] = str(jobcardObj.id)

	return dict

def paginate(jobcardsList, page_number):
    per_page = getattr(settings, 'JOB_CARDS_PER_PAGE', 100)
    paginator = Paginator(jobcardsList, per_page)
    if page_number is None:
        page = paginator.page(1)
    else:
        try:
            page = paginator.page(int(page_number))
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of
            # results.
            page = paginator.page(paginator.num_pages)
            return page, []
    return page, page.object_list
