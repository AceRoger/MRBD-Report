__author__ = 'vkm chandel'

SHOW_MONTH = 9

# GET_ROUTEMASTER_URL = "http://soatest.utility.esselgroup.com:8002/soa-infra/services/FieldMobility/getRouteMaster/getRouteMasterMediator_ep?WSDL"
# GET_ROUTEDETAILS_URL = "http://soatest.utility.esselgroup.com:8002/soa-infra/services/FieldMobility/getRouteDetails/getRouteDetails_ep?WSDL"
# UPLOADB30_URL = "http://soatest.utility.esselgroup.com:8002/soa-infra/services/FieldMobility/uploadMeterReading/uploadMeterReadingMediator_ep?WSDL"


#GET_ROUTEMASTER_URL = "http://soatest.utility.esselgroup.com:8002/soa-infra/services/FieldMobility/getRouteMaster!5.1*soa_d27a2a34-eac7-4b9e-be79-ed3212e8250a/getRouteMasterMediator_ep?WSDL"
#GET_ROUTEDETAILS_URL = "http://soatest.utility.esselgroup.com:8002/soa-infra/services/FieldMobility/getRouteDetails!5.1*soa_f594f698-c49e-4eae-8e88-00e14fe0172c/getRouteDetails_ep?WSDL"
#UPLOADB30_URL = ""

SERVER_URL='http://127.0.0.1:8000/'


def month_minus(yearMonth):
    try:
        #print 'In month_minus with ', yearMonth
        year=int(yearMonth[:-2])
        month=int(yearMonth[-2:])

        if month==1:
            year=year-1
            month=12
        else:
            month=month-1
        return str(year)+checkMonth(month)
    except Exception, e:
        print 'Exception|task.py|fail_downloadPN33', e
    return None


def month_plus(yearMonth):
    try:
        print 'In month_minus with ', yearMonth
        year=int(yearMonth[:-2])
        month=int(yearMonth[-2:])

        if month==12:
            year=year+1
            month=1
        else:
            month=month+1
        return str(year)+checkMonth(month)
    except Exception, e:
        print 'Exception|task.py|fail_downloadPN33', e
    return None


def checkMonth(month):
    if month > 9:
        return str(month)
    else:
        return '0' + str(month)
