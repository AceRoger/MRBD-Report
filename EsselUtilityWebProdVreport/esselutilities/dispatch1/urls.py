__author__ = 'Vijay/Shubham'

from.import views
from django.conf.urls import include, url

urlpatterns = [
    url(r'^dispatch-fil/(?P<billcycle_id>\d+)/$',views.get_dispatch),
    url(r'^dispatch-fil/(?P<billcycle_id>\d+)/(?P<month>\d+)/$',views.get_dispatch),
    url(r'^assign-mr/', views.assign_mr,name='assign_mr'),
    url(r'^deassign-mr/', views.deassign_mr,name='deassign_mr'),
    url(r'^get-jobcard/$',views.view_jobcard,name='view_jobcard'),
    url(r'^get-jobcard/(?P<month>\d+)/$',views.view_jobcard,name='view_jobcard'),
    url(r'^get-mr/$',views.get_mrlist,name='get_mrlist'),
    url(r'^save-data/', views.savedata),
    url(r'^savedata-billcycle/', views.savedata_billcycle),
    url(r'^revisit/(?P<billcycle_id>\d+)/(?P<month>\d+)/$', views.get_revisit),
    url(r'^get-jobcard-byfilter/', views.filter_jobcard,name='filter_jobcard'),
    url(r'^get-revisit-byfilter/', views.filter_revisit,name='filter_revisit'),
    url(r'^get-samemr/', views.assign_samemr),
    url(r'^search-mr/', views.search_mr, name='search_mr'),
    # url(r'^get-consumers-list/',views.get_consumers_list),
    url(r'^get-revisit-jobcard/(?P<billcycle_id>\d+)/(?P<month>\d+)/$', views.get_revisit_jobcard),
    url(r'^get-mr-revisit/$',views.get_mrlist_revisit,name='get_mrlist_revisit'),
    url(r'^get-samemr-revisit/', views.assign_samemr_revisit),
    url(r'^assign-mr-revisit/', views.assign_mr_revisit,name='assign_mr_revisit'),
    url(r'^search-mr-revisit/', views.search_mr_revisit, name='search_mr_revisit'),
    url(r'^get-mr-revisit-list/$',views.get_mrlist_revisit_list,name='get_mrlist_revisit_list'),
    url(r'^assign-mr-revisit-list/', views.assign_mr_revisit_list,name='assign_mr_revisit_list'),
    url(r'^deassign-mr-revisit/', views.deassign_mr_revisit,name='deassign_mr_revisit'),
    url(r'^revisit-list-exporttoexcel/(?P<billcycle_id>\d+)/(?P<bill_month>\d+)/$',views.revisit_list_exporttoexcel,name='revisit_list_exporttoexcel'),
    url(r'^refreshmrinfo/', views.refresh,name='refresh'),
]
