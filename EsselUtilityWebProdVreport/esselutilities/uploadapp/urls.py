__author__ = 'vkm chandel'

from django.conf.urls import include, url
from uploadapp.views import upload

urlpatterns = [
    url(r'^open-upload-index/', upload.open_upload_index, name='open_upload_index'),
    url(r'^open-reading/(?P<schedule_id>\d+)/$', upload.open_reading, name='open_reading'),
    url(r'^get-reading-list/', upload.get_reading_list, name='get_reading_list'),
    url(r'^get-upload-summery/', upload.get_upload_summery, name='get_upload_summery'),
    url(r'^export-b30-excel/(?P<upload_id>\d+)/$', upload.export_b30_excel, name='export_b30_excel'),
    url(r'^save-b30-table/', upload.save_b30_table, name='save_b30_table'),
    url(r'^get-bill-cycles-byfilter/',upload.get_bill_cycles_byfilter),
    url(r'^get-bill-cycles/',upload.get_bill_cycles),
    url(r'^get-upload-summery-by-route/', upload.get_upload_summery_by_route, name='get_upload_summery_by_route'),
    #url(r'^get-b30-images/(?P<upload_id>\d+)/$',upload.get_b30_images,name='get_b30_images'),
    url(r'^get-b30-images/(?P<upload_id>\d+)/$',upload.get_b30_images_url,name='get_b30_images'),
    url(r'^reading-export-to-excel/(?P<schedule_id>\d+)/$',upload.reading_export,name='reading_export'),

    url(r'^test/', upload.test, name='test'),




]




