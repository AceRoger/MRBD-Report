from django.contrib import admin
import models


# Register your models here.


class JobCardDetailAdmin(admin.ModelAdmin):
    list_display = (
    'id', 'routeassigned', 'consumerdetail', 'meterreader', 'reading_month', 'is_reading_completed', 'record_status')
    search_fields = ('consumerdetail', 'consumerdetail__bill_cycle__bill_cycle_code', 'reading_month')
    list_filter = (
    'consumerdetail__bill_cycle__bill_cycle_code', 'reading_month', 'is_reading_completed', 'is_active', 'is_revisit',
    'record_status')


class ReadingDetailAdmin(admin.ModelAdmin):
    list_display = (
    'id', 'jobcard', 'current_meter_reading', 'reader_status', 'reading_status', 'reading_month', 'reading_date',
    'latitude', 'longitude', 'Updated_on', 'is_deleted')
    search_fields = ('current_meter_reading', 'reader_status', 'reading_status', 'reading_month', 'Updated_on')
    list_filter = (
    'jobcard__consumerdetail__bill_cycle__bill_cycle_code', 'reading_status', 'meter_status__meter_status',
    'reading_month', 'is_deleted')


# class RouteAssignmentAdmin(admin.ModelAdmin):
#     list_display = ('id','routedetail__billcycle__bill_cycle_code','routedetail','reading_month','record_status','dispatch_status','is_reading_completed')
#     #search_fields = ('current_meter_reading','reader_status','reading_status','reading_month','Updated_on')
#     list_filter = ('routedetail__billcycle__bill_cycle_code','reading_month','is_reading_completed')
#
import csv
from django.http import HttpResponse

''' code for exporting excel starts'''
def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    def export_as_csv(modeladmin, request, queryset):
        """

        """
        opts = modeladmin.model._meta
        field_names = set([field.name for field in opts.fields])
        if fields:
            fieldset = set(fields)
            field_names = field_names & fieldset
        elif exclude:
            excludeset = set(exclude)
            field_names = field_names - excludeset
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % str(opts).replace('.', '_')
        writer = csv.writer(response)
        if header:
            writer.writerow([x for x in field_names])
        for obj in queryset:
            writer.writerow([str(getattr(obj, field)) for field in field_names])
        return response
    export_as_csv.short_description = description
    return export_as_csv



class AssignToValidator(admin.ModelAdmin):
    model = models.ValidatorAssignment
    # list_display = ('user','meterreading','remark','result','reading_month','is_validated','sent_to_revisit','meterreading__is_active','meterreading__is_duplicate','meterreading__is_deleted')
    list_display = (
    'get_bill_cycle', 'user', 'meterreading', 'remark', 'result', 'reading_month', 'is_validated', 'sent_to_revisit',
    'get_reading_status', 'get_is_duplicate', 'get_is_active', 'get_is_delete')
    list_filter = ('meterreading__jobcard__consumerdetail__bill_cycle__bill_cycle_code', 'meterreading__reading_status',
                   'meterreading__is_active', 'meterreading__is_duplicate', 'reading_month', 'is_validated', 'user')
    actions = [export_as_csv_action("Export selected student Records as CSV file", fields=list_display , header=False),]

    def get_bill_cycle(self, obj):
        return obj.meterreading.jobcard.consumerdetail.bill_cycle.bill_cycle_code

    def get_reading_status(self, obj):
        return obj.meterreading.reading_status

    def get_is_duplicate(self, obj):
        return obj.meterreading.is_duplicate

    def get_is_active(self, obj):
        return obj.meterreading.is_active

    def get_is_delete(self, obj):
        return obj.meterreading.is_deleted

    get_bill_cycle.short_description = 'bill cycle'
    get_reading_status.short_description = 'reading status'
    get_is_duplicate.short_description = 'is duplicate'
    get_is_active.short_description = 'is active'
    get_is_delete.short_description = 'is delete'




admin.site.register(models.RouteAssignment)
admin.site.register(models.JobCard, JobCardDetailAdmin)
admin.site.register(models.MeterStatus)
admin.site.register(models.ReaderStatus)
admin.site.register(models.MeterReading, ReadingDetailAdmin)
admin.site.register(models.ValidatorAssignment, AssignToValidator)
admin.site.register(models.ValidatorAssignmentCount)
admin.site.register(models.UnbilledConsumerAssignment)
admin.site.register(models.UnbilledConsumerAssignmentCount)
# admin.site.register(models.RouteProcess)
