from django.contrib import admin
import models

# Register your models here.


class RouteDetailAdmin(admin.ModelAdmin):
    list_display = ('id','route_code','billcycle','month','bill_month')
    search_fields = ('route_code','billcycle__bill_cycle_code','month','bill_month')
    list_filter = ('month','bill_month','billcycle',)


class UPLD_MTR_RDNG_Admin(admin.ModelAdmin):
    list_display = ('BILL_CYC','BILL_MONTH','CUSTOMER_ID','DOCUMENT_TYPE','DTR_NO','ESTIMATED','FEEDER_CODE','IMAGE_PATH','INSERTEDON','LATTITUDE','LONGITUDE','MDI','METER_READING','METER_STATUS','PC','PF','READER_ID','READING_DATE','ROUTE','SEQUENCE')
    search_fields = ('BILL_CYC','BILL_MONTH','CUSTOMER_ID','METER_STATUS','ROUTE')
    list_filter = ('BILL_CYC','BILL_MONTH',)



admin.site.register(models.UserPrivilege)
admin.site.register(models.UserRole)
admin.site.register(models.State)
admin.site.register(models.City)
admin.site.register(models.UserProfile)


admin.site.register(models.Utility)
admin.site.register(models.BillCycle)
#admin.site.register(models.PN33)
admin.site.register(models.RouteDetail,RouteDetailAdmin)
admin.site.register(models.EmployeeType)
admin.site.register(models.Availability)


admin.site.register(models.RT_MASTER)
admin.site.register(models.RT_DETAILS)
admin.site.register(models.UPLD_MTR_RDNG,UPLD_MTR_RDNG_Admin)

admin.site.register(models.Zone)
admin.site.register(models.Area)
admin.site.register(models.ApprovalDetails)
