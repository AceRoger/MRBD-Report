__author__ = 'vkm chandel'

from authenticateapp import views
from django.conf.urls import include, url

urlpatterns = [
    url(r'^$','authenticateapp.views.index',name='index'),
    url(r'^index/',views.index),
    # url(r'^welcome',views.welcome ),
    # url(r'^blank',views.blank ),
    url(r'^logout/',views.logout,name="logout" ),
    url(r'^login/',views.login),
    url(r'^forgot_pwd/',views.forgot_pwd),
    #url(r'^dashboard/',views.dashboard),
    # url(r'^consumer',views.consumer),
    url(r'^reset_pwd/',views.reset_pwd , name='reset_pwd'),
    url(r'^changepassword/', views.changepassword),
    url(r'^user_exist/',views.user_exist),
    # url(r'^applanding', views.applanding),
    url(r'^send_email/',views.send_email),

    url(r'^applicationlanding/', views.applicationlanding, name='applicationlanding'),
    url(r'^confirm_pwd/',views.confirm_pwd),
    # url(r'^users',views.users)
    # url(r'^get-dashboard/', views.get_dashboard),
]
