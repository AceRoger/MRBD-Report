from django.contrib import admin
import models

# Register your models here.

admin.site.register(models.BillSchedule)
admin.site.register(models.BillScheduleDetails)
admin.site.register(models.BillScheduleApprovalDetails)
admin.site.register(models.PN33Download)
admin.site.register(models.UploadB30)
