__author__ = 'Mayur Sable'

from scheduleapp.views import schedule,approval
from scheduleapp import helper
from django.conf.urls import include, url

urlpatterns = [
    url(r'^open-bill-schedule/', schedule.open_bill_schedule,name='open_bill_schedule'),
    url(r'^copy-from-previous/', schedule.copy_from_previous),
    url(r'^save-bill-schedule/', schedule.save_bill_schedule),
    url(r'^add-bill-cycle/', schedule.save_new_bill_cycle),
    url(r'^change-schedule/', schedule.change_schedule),
    url(r'^save-change-notConformed/', schedule.save_change_notConformed),
    url(r'^change-conformed-tab/', schedule.change_conformed_tab),
    url(r'^save-conformed-change/', schedule.save_conformed_change),
    url(r'^send-mail/', schedule.send_mail),
    url(r'^send-Reminder-Mail/', schedule.send_Reminder_Mail),
    url(r'^show-history/', schedule.show_history),
    url(r'^pending-history/', schedule.pending_history),
    url(r'^rejected-history/', schedule.rejected_history),
    url(r'^change-rejected-schedule/', schedule.change_rejected),
    url(r'^save-rejected-change/', schedule.save_rejected_change),
    url(r'^get-bill-schedules/', schedule.get_bill_schedules),
    url(r'^get-bill-schedules-byfilter/', schedule.get_bill_schedules_byfilter),
    url(r'^open-approval-index/',approval.open_approval_index, name='open-approval-index'),
    url(r'^approval-list/', approval.approval_list),
    url(r'^approval-Info/', approval.approval_Info),
    url(r'^approve-changes/', approval.approve_changes),
    url(r'^reject-changes/', approval.reject_changes),

    url(r'^get-dump/(?P<bill_month>\d+)/(?P<bill_cycle_code>\d+)/$', helper.get_dump, name='get-dump'),
    url(r'^get-unbilled-consumers/(?P<bill_month>\d+)/(?P<bill_cycle_code>\d+)/$', helper.get_unbilled_consumers, name='get-unbilled-consumers'),
    url(r'^get-all-consumer/(?P<bill_month>\d+)/(?P<from_date>\d+)/(?P<to_date>\d+)/$', helper.get_all_consumer, name='get-all-consumer'),

]
