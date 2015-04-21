"""
Views handling read (GET) requests for the Yammer Discussion tab.
"""

import json
import logging
import requests
from urlparse import urlparse
import yampy

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from edxmako.shortcuts import render_to_response
from courseware.courses import get_course_with_access
from opaque_keys.edx.keys import CourseKey

@login_required
def yammer(request, course_id):
    """
    Renders the Yammer Discussion page
    """
    course_key = CourseKey.from_string(course_id)
    course = get_course_with_access(request.user, 'load_forum', course_key, check_if_enrolled=True)

    network = request.user.social_auth.get(provider='yammer').extra_data['access_token']['network_name']

    feed_id = course.yammer_group_id # Yammer feed id is the same as the group id

    context = {
            'course': course,
            'course_id': course.id.to_deprecated_string(),
            'network': network,
            'feed_id': feed_id
        }

    return render_to_response('yammer/index.html', context)
