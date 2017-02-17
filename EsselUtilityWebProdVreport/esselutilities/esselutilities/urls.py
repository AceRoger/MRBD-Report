"""esselutilities URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url, patterns
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib import admin as djangoadmin
from adminapp import urls as adminappurl
from consumerapp import urls as consumerappurl
from authenticateapp import urls as authenticateappurl
from scheduleapp import urls as scheduleappurl
from validationapp import urls as validationappurl
from dispatch import urls as dispatchurl
from meterreaderapp import urls as meterreaderappurl
from mrbdapp import urls as mrbdappurl
from uploadapp import urls as uploadurl
from reportapp import urls as reportappurl



urlpatterns = [
    url(r'^$','authenticateapp.views.index',name='index'),
    url(r'^dashboard/$','authenticateapp.views.mrbd_dashboard',name='mrbd_dashboard'),
    url(r'^dashboard/(?P<month>\d+)/$','authenticateapp.views.mrbd_dashboard',name='mrbd_dashboard'),
    url(r'^django-admin/', include(djangoadmin.site.urls)),
    url(r'^admin/', include(adminappurl,namespace='adminapp')),
    url(r'^authen/',include(authenticateappurl,namespace='authen')),
    url(r'^consumer/', include(consumerappurl,namespace='consumer')),
    url(r'^schedule/', include(scheduleappurl,namespace='schedule')),
    url(r'^validate/',include(validationappurl,namespace='validate')),
    url(r'^dispatch/', include(dispatchurl,namespace='dispatch')),
    url(r'^meterreader/', include(meterreaderappurl,namespace='meterreader')),
    url(r'^api/', include(mrbdappurl,namespace='mrbdapp')),
    url(r'^upload/', include(uploadurl, namespace='upload')),
    url(r'^report/', include(reportappurl, namespace='report')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns = patterns('',
#     (r'^$',include(authenticateappurl)),
#     (r'^django-admin/', include(djangoadmin.site.urls)),
#     (r'^admin/', include(adminappurl,namespace='adminapp')),
#     (r'^authen/',include(authenticateappurl,namespace='authen')),
#     (r'^consumer/', include(consumerappurl,namespace='consumer')),
#     (r'^schedule/', include(scheduleappurl,namespace='schedule')),
#     (r'^validate/',include(validationappurl,namespace='validate')),
#     (r'^dispatch/', include(dispatchurl,namespace='dispatch')),
#     (r'^meterreader/', include(meterreaderappurl,namespace='meterreader')),
#     (r'^api/', include(mrbdappurl,namespace='mrbdapp')),
# ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
