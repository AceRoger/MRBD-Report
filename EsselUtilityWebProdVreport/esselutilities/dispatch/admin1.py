from django.contrib import admin
import models
# Register your models here.


class JobCardDetailAdmin(admin.ModelAdmin):
    list_display = ('id','routeassigned','consumerdetail','meterreader','reading_month','is_reading_completed','record_status')
    search_fields = ('consumerdetail','consumerdetail__bill_cycle__bill_cycle_code','reading_month')
    list_filter = ('consumerdetail__bill_cycle__bill_cycle_code','reading_month','is_reading_completed','is_active','is_revisit','record_status')


class ReadingDetailAdmin(admin.ModelAdmin):
    list_display = ('id','jobcard','current_meter_reading','reader_status','reading_status','reading_month','reading_date','latitude','longitude','Updated_on','is_deleted')
    search_fields = ('current_meter_reading','reader_status','reading_status','reading_month','Updated_on')
    list_filter = ('jobcard__consumerdetail__bill_cycle__bill_cycle_code','reading_status','meter_status__meter_status','reading_month','is_deleted')

# class RouteAssignmentAdmin(admin.ModelAdmin):
#     list_display = ('id','routedetail__billcycle__bill_cycle_code','routedetail','reading_month','record_status','dispatch_status','is_reading_completed')
#     #search_fields = ('current_meter_reading','reader_status','reading_status','reading_month','Updated_on')
#     list_filter = ('routedetail__billcycle__bill_cycle_code','reading_month','is_reading_completed')
#



admin.site.register(models.RouteAssignment)
admin.site.register(models.JobCard,JobCardDetailAdmin)
admin.site.register(models.MeterStatus)
admin.site.register(models.ReaderStatus)
admin.site.register(models.MeterReading,ReadingDetailAdmin)
admin.site.register(models.ValidatorAssignment)
admin.site.register(models.ValidatorAssignmentCount)
admin.site.register(models.UnbilledConsumerAssignment)
admin.site.register(models.UnbilledConsumerAssignmentCount)
#admin.site.register(models.RouteProcess)