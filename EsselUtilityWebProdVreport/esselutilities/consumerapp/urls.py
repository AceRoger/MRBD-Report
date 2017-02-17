__author__ = 'vkm chandel'

from django.conf.urls import include, url
from consumerapp.views import pn33,consumer
from consumerapp import helper

urlpatterns = [
    url(r'^open-pn33-index/', pn33.open_pn33_index, name='open_pn33_index'),
    url(r'^import-pn33/',pn33.import_pn33),
    url(r'^get-bill-cycles/',pn33.get_bill_cycles),
    url(r'^get-bill-cycles-byfilter/',pn33.get_bill_cycles_byfilter),
    #url(r'^get-mr/(?P<route_id>\d+)/$',views.get_mrlist),
    #url(r'^open-consumer-index/(?P<billcycle_code>\d+)/(?P<billcycle_id>\d+)/$', consumer.open_consumer_index, name='open_consumer_index'),
    url(r'^open-consumer-index/(?P<bill_schedule_id>\d+)/$', consumer.open_consumer_index, name='open_consumer_index'),
    url(r'^get-consumers-list/', consumer.get_consumers_list),
    url(r'^get-consumer-details/', consumer.get_consumer_details),
    url(r'^reading-export-to-excel/(?P<schedule_id>\d+)/$',consumer.reading_export,name='reading_export'),

    url(r'^read-excel/', helper.read_exl),
    url(r'^check-reading/', helper.check_reading),
    url(r'^check-consumer12digit/', helper.consumer_id_12digit),

]




