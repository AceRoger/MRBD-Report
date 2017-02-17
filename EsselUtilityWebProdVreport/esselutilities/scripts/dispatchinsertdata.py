
import datetime
from django.core.management import call_command
from adminapp.models import State,City,Utility,EmployeeType,UserProfile,UserPrivilege,UserRole,BillCycle,RouteDetail
from consumerapp.models import ConsumerDetails
from scheduleapp.models import PN33Download,BillSchedule
from meterreaderapp.models import DeviceDetail
from dispatch.models import RouteAssignment,JobCard

privileges=['Dashboard','Import PN33','Schedule','Dispatch','Validation1','Validation2','Approve schedule','Upload','System User','Administration']


def run():
    today = datetime.date.today()
    utility = Utility(
        utility='Electricity',
        created_by='admin',
        updated_by='admin',
        created_date=today,
        updated_date=today,
        is_deleted='False'

    )
    utility.save()
    for i in range(1, 2):
        state = State(
            state='Maharashtra',
            created_by='admin',
            updated_by='admin',
            created_date=today,
            updated_date=today,
            is_deleted='False'

        )
        state.save()
        print state

        for j in range(1, 2):
            city = City(
                city='Akola',
                state=state,
                created_by='admin',
                updated_by='admin',
                created_date=today,
                updated_date=today,
                is_deleted='False'

            )
            city.save()
            print city

            for k in range(200, 205):
                billcycle = BillCycle(
                    bill_cycle_code=k,
                    city=city,
                    utility=utility,
                    created_by='admin',
                    updated_by='admin',
                    created_date=today,
                    updated_date=today,
                    is_deleted='False'
                )
                billcycle.save()
                print billcycle

                for l in range(1000, 1010):
                    routedetail = RouteDetail(
                        route_code=l,
                        billcycle=billcycle,
                        record_status='Active',
                        created_by='admin',
                        updated_by='admin',
                        created_on=today,
                        updated_on=today
                    )
                    routedetail.save()
                    print routedetail

                    for c in range(1, 50):
                        consumer = ConsumerDetails(
                            name='shubham' + str(c),
                            # consumer_last_name='pawar',
                            email_id='shubham.pawar' + str(c) + '@bynry.com',
                            contact_no='8007271913',
                            address_line_1="ABC Road",
                            address_line_2='Mumbai',
                            city=city,
                            pin_code='222343',
                            route=routedetail,
                            bill_cycle=billcycle,
                            meter_no='688686',
                            dtc='123',
                            pole_no='88888',
                            month=today,
                            is_deleted='No',
                            created_by='admin',
                            updated_by='admin',
                            created_date=today,
                            updated_date=today,
                        )
                        consumer.save()


#
# def savedata(request):
#
#     today = datetime.date.today()
#     billcycle=BillCycle.objects.get(bill_cycle_code=201)
#     print 'shubham'
#     for i in range(1,2):
#         billSchedule = BillSchedule(
#
#             bill_cycle=billcycle,
#             month=today,
#             start_date=today,
#             end_date=today + datetime.timedelta(30),
#             accounting_date=today,
#             estimated_date=today,
#             version='first',
#             status='Confirmed',
#             created_by='admin',
#             updated_by='admin',
#             created_date=today,
#             updated_date=today,
#             is_deleted='No'
#         )
#         billSchedule.save()
#         print billSchedule
#
#         pn33 = PN33Download(
#
#
#             bill_schedule=billSchedule,
#             month=today,
#             start_date=today,
#             end_date=today + datetime.timedelta(30),
#             download_status='COMPLETED',
#             created_by='admin',
#             updated_by='admin',
#             created_date=today,
#             updated_date=today,
#             is_deleted='No'
#
#         )
#         pn33.save()
#
#     return render(request, 'dispatch/dis.html')


def savedata(request):

    today = datetime.date.today()
    employetype = EmployeeType(

        employee_type='permanant',
        created_by='admin',
        updated_by='admin',
        created_date=today,
        updated_date=today,
        is_deleted='False'

    )
    employetype.save()
    print employetype
    for privilege in privileges:
        userprivilege = UserPrivilege(
                privilege=privilege,
                created_by='admin',
                updated_by='admin',
                created_date=today,
                updated_date=today,
                is_deleted='False'

        )
        userprivilege.save()
    print userprivilege


    userrole = UserRole(
                    role='MeterReader',
                    description='metereader',
                    status='ACTIVE',
                    created_by='admin',
                    updated_by='admin',
                    created_date=today,
                    updated_date=today,
                    is_deleted='False'
            )


    userrole.save()
    print  userrole

    # state = State.objects.get(state='Maharashtra')
    # city = City.objects.get(city='Akola')
    # for i in range (1,21):
    #     userprofile = UserProfile(
    #         username='shubhampawar' +str(i) + '@bynry.com',
    #         first_name='shubham'+ str(i),
    #         email_address='shubhampawar'+str(i) + '@bynry.com',
    #         date_joined=today,
    #         contact_no='8007271914',
    #         last_name='pawar'+str(i),
    #         address_line_1='abc',
    #         address_line_2='Akola',
    #         city=city,
    #         state=state,
    #         pincode="123123",
    #         role=userrole,
    #         employee_id='123',
    #         employee_type=employetype,
    #         type='METER_READER',
    #         status='Active',
    #         updated_by='admin',
    #         created_date=today,
    #         updated_date=today,
    #         is_deleted='False'
    #     )
    #     userprofile.save()
    #     print userprofile
    #
    #     devicedetail = DeviceDetail(
    #     company_name='Essel',
    #     device_name='Samsung',
    #     make='Essel',
    #     imei_no='12340' + str(i),
    #     user=userprofile,
    #     is_deleted='No',
    #     device_details_created_by='admin',
    #     device_details_updated_by='admin',
    #     device_details_created_date=today,
    #     device_details_updated_date=today
    #     )
    #
    #     devicedetail.save()

    # for i in range(1000,1005):

    #     billCycle=BillCycle.objects.get(bill_cycle_code=201)
    #     print 'shubham'
    #     routedetail = RouteDetail.objects.get(billcycle=billCycle,route_code=i)

    #     userprofile = UserProfile.objects.get(userprofile_id=7)
    #     routeAssignment = RouteAssignment(
    #         routedetail=routedetail,
    #         userprofile=userprofile,
    #         assign_date=today,
    #         due_date=today,
    #         reading_month='Aug',
    #         is_deleted='No',
    #         record_status='Active',
    #         created_by='admin',
    #         updated_by='admin',
    #         created_on=today,
    #         updated_on=today,
    #     )
    #     routeAssignment.save()
    #     print routeAssignment

    #     consumer = ConsumerDetails.objects.get(bill_cycle=201)
    #     jobcard = JobCard(
    #         meterdetail=consumer,
    #         user=userprofile,
    #         assigned_date=today,
    #         completion_date=today,
    #         is_deleted='No',
    #         record_status='Active',
    #         created_by='admin',
    #         updated_by='admin',
    #         created_on=today,
    #         updated_on=today,
    #     )
    #     jobcard.save()


    #
    #     devicedetail = DeviceDetail(
    #
    #         company_name='aaaaa',
    #         device_name='bbbb',
    #         make='acb',
    #         imei_no='123444444444',
    #         user=userprofile,
    #         is_deleted='No',
    #         device_details_created_by='admin',
    #         device_details_updated_by='admin',
    #         device_details_created_date=today,
    #         device_details_updated_date=today
    #
    #     )
    #     devicedetail.save()

#
#     devicedetail.save()
#
# def meterstatus(request):
#     meterstatus=MeterStatus(
#         meter_status='Normal',
#         is_deleted='No',
#         record_status='Active',
#         created_by='admin',
#         updated_by='admin',
#         created_on=today,
#         updated_on=today,
#
#
#     )
#     meterstatus.save()
#
#     reader_status=ReaderStatus(
#         reader_status='Normal',
#         is_deleted='No',
#         record_status='Active',
#         created_by='admin',
#         updated_by='admin',
#         created_on=today,
#         updated_on=today,
#
#     )





