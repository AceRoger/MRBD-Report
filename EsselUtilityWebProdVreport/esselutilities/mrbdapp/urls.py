from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^login$', views.login, name='login'),
	url(r'^get_job_cards$', views.get_job_cards, name='get_job_cards'),
	url(r'^get_job_cards/(?P<page_number>\d+)/$', views.get_job_cards, name='get_job_cards'),
	url(r'^get_dr_job_cards/(?P<page_number>\d+)/$', views.get_deassigned_reassigned_job_cards, name='get_deassigned_reassigned_job_cards'),
	url(r'^get_deassigned_reassigned_job_cards$', views.get_deassigned_reassigned_job_cards, name='get_deassigned_reassigned_job_cards'),
	url(r'^get_deassigned_reassigned_job_cards/(?P<page_number>\d+)/$', views.get_deassigned_reassigned_job_cards, name='get_deassigned_reassigned_job_cards'),
	url(r'^add_new_consumer$', views.add_new_consumer, name='add_new_consumer'),
	url(r'^upload_meter_reading$', views.upload_meter_reading, name='upload_meter_reading'),
	url(r'^update_user_profile$', views.update_user_profile, name='update_user_profile'),
	url(r'^update_push_token$', views.update_push_token, name='update_push_token'),
	url(r'^logout$', views.logout, name='logout'),
	]