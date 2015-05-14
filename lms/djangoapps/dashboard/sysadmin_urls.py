"""
Urls for sysadmin dashboard feature
"""
# pylint: disable=no-value-for-parameter

from django.conf.urls import patterns, url, include

from dashboard import sysadmin
from azuread import views


urlpatterns = patterns(
    '',
    url(r'^$', sysadmin.Users.as_view(), name="sysadmin"),
    url(r'^courses/?$', sysadmin.Courses.as_view(), name="sysadmin_courses"),
    url(r'^staffing/?$', sysadmin.Staffing.as_view(), name="sysadmin_staffing"),
    url(r'^gitlogs/?$', sysadmin.GitLogs.as_view(), name="gitlogs"),
    url(r'^gitlogs/(?P<course_id>.+)$', sysadmin.GitLogs.as_view(),
        name="gitlogs_detail"),

    url(r"^azuread/?$", views.AzureADMain.as_view(), name="azuread_main"),		
    url(r"^azuread/users/?$", views.AzureADUsers.as_view(), name="azuread_users"),		
    url(r"^azuread/users/changestatus$", views.azure_user_changestatus, name="azuread_users_changestatus"),		
    url(r"^azuread/users/create/?$", views.AzureADCreateUser.as_view(), name="azuread_create_user"),    
    url(r"^azuread/users/edit/?$", views.AzureADEditUser.as_view(), name="azuread_users_edit"),    

)
