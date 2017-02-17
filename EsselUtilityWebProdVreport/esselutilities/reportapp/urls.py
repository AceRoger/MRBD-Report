
from django.conf.urls import include, url
from reportapp import views

urlpatterns = [
    url(r'^records-landing-page/',views.records_landing_page,name='records_landing_page'),
    url(r'^performance-report/',views.performance_report,name='performance-report'),

]

