from django.test import TestCase

# Create your tests here.


# def get_reading_list(request):
#     try:
#         # pdb.set_trace()
#         consumerList = []
#         print 'request.GET', request.GET
#         column = request.GET.get('order[0][column]')
#         searchTxt = request.GET.get('search[value]')
#         order = ""
#         if request.GET.get('order[0][dir]') == 'desc':
#             order = "-"
#
#         list = ['route__route_code', 'consumer_no', 'meter_no', 'name']
#         column_name = order + list[int(column)]
#
#         start = request.GET.get('start')
#         length = int(request.GET.get('length')) + int(request.GET.get('start'))
#         route_code = request.GET.get('route_code')
#         reading_status = request.GET.get('readingStatus')
#         billSchedule = BillSchedule.objects.get(id=request.GET.get('billSchedule'))
#
#         billScheduleDetails = BillScheduleDetails.objects.get(billSchedule=billSchedule, last_confirmed=True)
#         billCycle = billSchedule.bill_cycle
#
#         # ,Q(month=constraints.month_minus(billSchedule.month))
#         # Q(month=constraints.month_minus(billSchedule.month)),
#
#         if route_code == 'All':
#             total_record = ConsumerDetails.objects.filter(bill_cycle=billCycle, is_deleted=False,
#                                                           month=constraints.month_minus(billSchedule.month)).count()
#
#             print 'total_record', total_record
#             consumerDetails = ConsumerDetails.objects.filter(Q(bill_cycle=billCycle),
#                                                              Q(month=constraints.month_minus(billSchedule.month)),
#                                                              Q(consumer_no__contains=searchTxt) | Q(
#                                                                  meter_no__contains=searchTxt) | Q(
#                                                                  name__contains=searchTxt)).order_by(column_name)[
#                               start:length]
#
#         else:
#             routeDetail = RouteDetail.objects.get(id=route_code)
#             total_record = ConsumerDetails.objects.filter(route=routeDetail, bill_cycle=billCycle,
#                                                           month=constraints.month_minus(billSchedule.month),
#                                                           is_deleted=False).count()
#
#             consumerDetails = ConsumerDetails.objects.filter(Q(bill_cycle=billCycle), Q(route=routeDetail),
#                                                              Q(month=constraints.month_minus(billSchedule.month)),
#                                                              Q(consumer_no__contains=searchTxt) | Q(
#                                                                  meter_no__contains=searchTxt) | Q(
#                                                                  name__contains=searchTxt)).order_by(column_name)[
#                               start:length]
#
#
#
#
#             # consumerDetails = ConsumerDetails.objects.filter(Q(route=routeDetail), Q(bill_cycle=billCycle),
#             #                                                  Q(name__contains=searchTxt) |
#             #                                                  Q(address_line_1__contains=searchTxt) |
#             #                                                  Q(address_line_1__contains=searchTxt) |
#             #                                                  Q(contact_no__contains=searchTxt)).order_by(column_name)[
#             #                   start:length]
#
#         if reading_status == 'All':
#             consumerDetails = consumerDetails
#         elif reading_status == 'ReadingTaken':
#             consumerDetails = consumerDetails.filter(id__id=[jobCard.consumerdetail.id for jobCard in
#                                                              JobCard.objects.filter(is_active=True,
#                                                                                     reading_month=billSchedule.month,
#                                                                                     is_reading_completed=True)])
#         elif reading_status == 'ReadingNotTaken':
#             consumerDetails = consumerDetails.filter(id__id=[jobCard.consumerdetail.id for jobCard in
#                                                              JobCard.objects.filter(is_active=True,
#                                                                                     reading_month=billSchedule.month,
#                                                                                     is_reading_completed=False)])
#
#         meterReadings = MeterReading.objects.filter(jobcard__consumerdetail__bill_cycle=billCycle,
#                                                     current_meter_reading=billSchedule.month)
#
#         due_data = billScheduleDetails.end_date.strftime('%d/%m/%Y')
#
#         print 'consumerDetails', consumerDetails
#
#         for consumerDetail in consumerDetails:
#             tempList = []
#             reading_status = meterReadings.filter(jobcard__consumerdetail__id=consumerDetail.id)
#
#             tempList.append(consumerDetail.route.route_code)
#             tempList.append(consumerDetail.consumer_no)
#             tempList.append(consumerDetail.meter_no)
#             tempList.append(consumerDetail.name)
#
#             if reading_status:
#                 tempList.append(reading_status[0].reading_status)
#             else:
#                 tempList.append('Not Taken')
#
#             tempList.append(due_data)
#             if reading_status:
#                 tempList.append(reading_status[0].reading_date)
#             else:
#                 tempList.append('----')
#
#             tempList.append('---')
#
#             consumerList.append(tempList)
#         data = {'iTotalRecords': total_record, 'iTotalDisplayRecords': total_record, 'aaData': consumerList}
#         print 'data', data
#     except Exception, e:
#         print 'Exception|upload.py|get_reading_list', e
#         data = {'success': 'false'}
#     return HttpResponse(json.dumps(data), content_type='application/json')
