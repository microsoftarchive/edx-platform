"""
URLs for AzureAD.
"""
from django.conf.urls import patterns, url

urlpatterns = patterns(
    "azuread.views",
    url(r"^/admin/azuread/users$", "users_list", name="azuread_users"),

)
