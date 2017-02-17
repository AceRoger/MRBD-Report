__author__ = 'vkm chandel'


from adminapp.views import user,role
from django.conf.urls import include, url

urlpatterns = [
    # url(r'^open-user-index/',user.open_user_index),
    url(r'^open-role-index/',role.open_role_index, name='open_role_index'),
    url(r'^save-user-role/',role.save_user_role),
    url(r'^list-user-role/',role.list_user_role),
    url(r'^view-edit-role/',role.view_edit_role),
    url(r'^update-user-role/',role.update_user_role),
    url(r'^record-status-change/',role.record_status_change),

    # url(r'^save-user/',user.save_user),
    # url(r'^list-user/',user.list_user),
    # url(r'^view-user/',user.view_user),
]

