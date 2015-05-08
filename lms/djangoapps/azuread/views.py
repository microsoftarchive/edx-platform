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

from edxmako.shortcuts import render_to_response



from django.contrib.auth.decorators import user_passes_test



logger = logging.getLogger(__name__)


@user_passes_test(lambda u: u.is_superuser)
def users_list(request):
    """
    Displays the AAD users list.
    """

    from azuread.getfeed import getFeed

    try:
        users_json = getFeed("users")
        data = json.loads(users_json)
        users = data["value"]
    except Exception(e):
        users = None


    print users

    context = {
        "users": users,
    }

    return render_to_response("azuread/admin/users_list.html", context)

