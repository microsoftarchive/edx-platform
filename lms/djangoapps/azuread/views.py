"""URL handlers related to certificate handling by LMS"""
from datetime import datetime
import dogstats_wrapper as dog_stats_api
import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.utils.translation import ugettext as _
from django.shortcuts import redirect
from edxmako.shortcuts import render_to_response

from dashboard.sysadmin import SysadminDashboardView


from django.contrib.auth.decorators import user_passes_test
import os

from azuread.authAAD import AuthorizationHelperForAADGraphService


logger = logging.getLogger(__name__)

class AzureADMain(SysadminDashboardView):

    template_name = 'azuread/admin/azuread_main.html'


    def get(self, request):

        if not request.user.is_staff:
            raise Http404
        #this context, and several more below, are built with the 
        #basic info that the dashboard templates require
        
        context = {
            'datatable': self.datatable,
            'msg': self.msg,
            'djangopid': os.getpid(),
            'modeflag': {'azuread': 'active-section'},
            'edx_platform_version': getattr(settings, 'EDX_PLATFORM_VERSION_STRING', ''),
        }
        return render_to_response(self.template_name, context)



class AzureADEditUser(SysadminDashboardView):
    template_name = 'azuread/admin/azuread_userform.html'

    def get(self, request):

        if not request.user.is_staff:
            raise Http404
        auth = AuthorizationHelperForAADGraphService()

        context = {
            'datatable': self.datatable,
            'msg': self.msg,
            'djangopid': os.getpid(),
            'modeflag': {'azuread': 'active-section'},
            'edx_platform_version': getattr(settings, 'EDX_PLATFORM_VERSION_STRING', ''),
            'azuread_domain': settings.SOCIAL_AUTH_AZURE_DOMAIN,
            'form_data': {},
            'is_edit': True,
        }

        user_id = request.GET.get("id","")
        if user_id == "":
            return redirect("azuread_users")
        user_data = json.loads(auth.get_user(user_id))


        #build dict for html data, this will be used in the form to show current values
        form_data = {}

        form_data["firstname"] = user_data["givenName"]
        form_data["lastname"] = user_data["surname"]
        form_data["displayname"] = user_data["displayName"]
        form_data["object_id"] = user_id

        if user_data["userPrincipalName"].find("#EXT#") > -1:
            form_data["email"] = user_data["otherMails"][0]
        else:
            form_data["email"] = user_data["userPrincipalName"]


        #clear all the Nones, put empty strings for better handling
        for k in form_data:
            if form_data[k] == None:
                form_data[k] = ""
        context["form_data"] = form_data


        return render_to_response(self.template_name, context)

    def post(self, request):

        if not request.user.is_staff:
            raise Http404


        user_id = request.POST.get("object_id","")


        auth = AuthorizationHelperForAADGraphService()

        context = {
            'datatable': self.datatable,
            'msg': self.msg,
            'djangopid': os.getpid(),
            'modeflag': {'azuread': 'active-section'},
            'edx_platform_version': getattr(settings, 'EDX_PLATFORM_VERSION_STRING', ''),
            'azuread_domain': settings.SOCIAL_AUTH_AZURE_DOMAIN,
            'form_data': {},
            'is_edit': True,
        }


        #create new edit dictionary
        new_data = {}
        new_data["givenName"] = request.POST.get("firstname","")
        new_data["surname"] = request.POST.get("lastname","")
        new_data["displayName"] = request.POST.get("displayname","")

        password = request.POST.get("password","")
        if password != "":
            new_data["passwordProfile"] = {"password":password,"forceChangePasswordNextLogin":False}

        auth = AuthorizationHelperForAADGraphService()

        returned = auth.update_user(user_id, new_data)
        
        data_returned = json.loads(returned)

        #check for errors, replace some common azure strings.
        has_error = False
        if data_returned.has_key("odata.error"):
            replace_vars = {}
            replace_vars["userPrincipalName"] = "username"
            replace_vars["surname"] = "last name"
            replace_vars["givenName"] = "first name"
            replace_vars["displayName"] = "first or last name"
            replace_vars["mailNickname"] = "username"

            context["msg"] = data_returned["odata.error"]["message"]["value"]

            has_error = True
            for k in replace_vars:
                context["msg"] = context["msg"].replace(k, replace_vars[k])

        if has_error:
            context["form_data"] = request.POST
            return render_to_response(self.template_name, context)
        else:
            context["form_data"] = {}
            return redirect("azuread_users")




class AzureADCreateUser(SysadminDashboardView):

    template_name = 'azuread/admin/azuread_userform.html'

    def get(self, request):

        if not request.user.is_staff:
            raise Http404
        auth = AuthorizationHelperForAADGraphService()



        context = {
            'datatable': self.datatable,
            'msg': self.msg,
            'djangopid': os.getpid(),
            'modeflag': {'azuread': 'active-section'},
            'edx_platform_version': getattr(settings, 'EDX_PLATFORM_VERSION_STRING', ''),
            'azuread_domain': settings.SOCIAL_AUTH_AZURE_DOMAIN,
            'form_data': {},
            'is_edit': False,

        }

        return render_to_response(self.template_name, context)

    def post(self, request):

        if not request.user.is_staff:
            raise Http404

        auth = AuthorizationHelperForAADGraphService()

        context = {
            'datatable': self.datatable,
            'msg': self.msg,
            'djangopid': os.getpid(),
            'modeflag': {'azuread': 'active-section'},
            'edx_platform_version': getattr(settings, 'EDX_PLATFORM_VERSION_STRING', ''),
            'azuread_domain': settings.SOCIAL_AUTH_AZURE_DOMAIN,
        }
        auth = AuthorizationHelperForAADGraphService()


        #create new dictionary with user data to pass to azure methods
        user_data = {}
        user_data["username"] = request.POST.get("username","")
        user_data["password"] = request.POST.get("password","")
        user_data["givenName"] = request.POST.get("firstname","")
        user_data["surname"] = request.POST.get("lastname","")
        user_data["fullname"] = request.POST.get("displayname","")
        returned = auth.create_user(user_data)

        data_returned = json.loads(returned)

        # check for errors, replace some common azure strings with more user-readable strings.
        has_error = False
        if data_returned.has_key("odata.error"):
            replace_vars = {}
            replace_vars["userPrincipalName"] = "username"
            replace_vars["surname"] = "last name"
            replace_vars["givenName"] = "first name"
            replace_vars["displayName"] = "first or last name"
            replace_vars["mailNickname"] = "username"

            context["msg"] = data_returned["odata.error"]["message"]["value"]
            has_error = True
            for k in replace_vars:
                context["msg"] = context["msg"].replace(k, replace_vars[k])

        if has_error:
            context["form_data"] = request.POST
            return render_to_response(self.template_name, context)
        else:
            context["form_data"] = {}
            return redirect("azuread_users")


class AzureADUsers(SysadminDashboardView):
    template_name = 'azuread/admin/azuread_users.html'


    def get(self, request):

        if not request.user.is_staff:
            raise Http404

        from azuread.getfeed import getFeed

        try:
            users_json = getFeed("users")

            data = json.loads(users_json)
            users = data["value"]
        except Exception:
            users = []



        self.datatable = {'data':users}
        context = {
            'datatable': self.datatable,
            'msg': self.msg,
            'djangopid': os.getpid(),
            'modeflag': {'azuread': 'active-section'},
            'edx_platform_version': getattr(settings, 'EDX_PLATFORM_VERSION_STRING', ''),
        }
        return render_to_response(self.template_name, context)


#this is a basic method to just change the user status, from enabled to disabled.
def azure_user_changestatus(request):

    #if user is not staff, just 404 on them.
    if not request.user.is_staff:
        raise Http404

    user_id = request.GET.get("id","")
    if(user_id == ""):
        return redirect("azuread_users")

    new_status =  request.GET.get("a","")
    if new_status == "":
        return redirect("azuread_users")

    new_data = {}
    if new_status ==  "d":
        new_data["accountEnabled"] = False

    if new_status ==  "a":
        new_data["accountEnabled"] = True

    auth = AuthorizationHelperForAADGraphService()
    auth.update_user(user_id, new_data)
    return redirect("azuread_users")


