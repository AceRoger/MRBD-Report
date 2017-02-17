# from esselutilities.meterreaderapp.views import addmr

__author__ = 'shubham joshi'
from adminapp.views import user,role

from meterreaderapp.views import systemuser
from meterreaderapp.views import detailmr
from meterreaderapp.views import detailvalidator
from meterreaderapp.views import detailadmin
from meterreaderapp.views import trackmr
from django.conf.urls import include, url

urlpatterns = (
    url(r'^open-systemuser-index/$', systemuser.get_user_list, name='open-systemuser-index'),
    # url(r'^open-systemuser-index/(?P<month>\d+)/$', systemuser.get_user_list, name="open-systemuser-index"),

    url(r'^save-mr/', systemuser.save_mr),
    url(r'^edit-save-approver/', systemuser.edit_save_approver),
    url(r'^save-validator/', systemuser.save_validtor),
    url(r'^save-admin/', systemuser.save_admin),
    url(r'^get-route/', systemuser.get_route),
    url(r'^change-user-status/', systemuser.change_user_status),
    url(r'^refreshmrinfo/', systemuser.refresh),
    url(r'^view-edit-approval/', systemuser.view_edit_approval),

    #url(r'^get-user-list/(?P<mr_id>\d+)/(?P<month>\d+)/$',systemuser.get_user_list),

    url(r'^update-availability/', detailmr.update_availability),
    url(r'^detail-mr/(?P<mr_id>\d+)/$', detailmr.detail_mr),
    url(r'^detail-mr/(?P<mr_id>\d+)/(?P<month>\d+)/$', detailmr.detail_mr),

    url(r'^get-meterreader/', detailmr.get_meterreader),
    url(r'^detail-track-mr/(?P<mr_id>\d+)/$', trackmr.track_mr),
    url(r'^get-bill-cycle/', trackmr.get_cycle),
    url(r'^get-route-for-track/', trackmr.get_routes),

    url(r'^detail-validator/(?P<validator_id>\d+)/$', detailvalidator.detail_validator),
    url(r'^detail-validator/(?P<validator_id>\d+)/(?P<month>\d+)/$',detailvalidator.detail_validator),
    url(r'^detail-admin/(?P<admin_id>\d+)/$',detailadmin.detail_admin),
    # url(save-mr link call from ajax/addmr-(views.pyfile name).save_mr is link name on views file
    url(r'^get-validator/', detailvalidator.get_validator),

    url(r'^edit-save-mr/', detailmr.edit_save_mr),
    url(r'^edit-save-validator/', detailvalidator.edit_save_validator),
    url(r'^update-validator-availability/', detailvalidator.update_validator_availability),
    url(r'^edit-save-admin/', detailadmin.edit_save_admin),
    url(r'^reading-export-to-excel-meterreader/(?P<mr_id>\d+)/(?P<currentmonth>\d+)/$', detailmr.reading_export_materreader, name='reading_export_materreader'),
    url(r'^reading-export-to-excel-validator/(?P<validator_id>\d+)/(?P<currentmonth>\d+)/$', detailvalidator.reading_export_validator, name='reading_export_validator'),
    # url(r'^reading-export-to-excel-systmuser/(?P<currentmonth>\d+)/$',systemuser.reading_export_systemuser,name='reading_export_systemuser'),
    url(r'^reading-export-to-excel-systemuser/',systemuser.reading_export_systemuser,name='reading_export_systemuser'),
    url(r'^get-route-path/', trackmr.get_route_path),
)
