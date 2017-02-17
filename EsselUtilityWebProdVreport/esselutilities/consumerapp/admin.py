from django.contrib import admin
from consumerapp import models



class ConsumerDetailAdmin(admin.ModelAdmin):
    list_display = ('id','consumer_no','name','route','bill_cycle','bill_month')
    search_fields = ('consumer_no','name','route__route_code','bill_cycle__bill_cycle_code','bill_month')
    list_filter = ('bill_month','bill_cycle__bill_cycle_code','route__route_code',)

admin.site.register(models.ConsumerDetails,ConsumerDetailAdmin)
admin.site.register(models.UnBilledConsumers)
# Register your models here.
