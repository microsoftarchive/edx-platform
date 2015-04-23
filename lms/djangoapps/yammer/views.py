"""
Views handling read (GET) requests for the Yammer Discussion tab.
"""

import json
import logging
import requests

from django.contrib.auth.decorators import login_required

from edxmako.shortcuts import render_to_response
from courseware.courses import get_course_with_access
from opaque_keys.edx.keys import CourseKey

yammer_api = 'https://www.yammer.com/api/v1/'

@login_required
def yammer(request, course_id):
    """
    Renders the Yammer Discussion page
    """
    course_key = CourseKey.from_string(course_id)
    course = get_course_with_access(request.user, 'load_forum', course_key, check_if_enrolled=True)

    try:
        yammer_social_user = request.user.social_auth.get(provider='yammer')
        token = yammer_social_user.extra_data['access_token']
    except:
        context = {
                'course': course,
                'course_id': course.id.to_deprecated_string(),
            }
        return render_to_response('yammer/index.html', context)

    # TODO: Possibly a better place to do the following is when the user enrols into the course, but that would require
    # the enrollment procedure to fire an event so we can do this in the event handler. Since that is not
    # happening right now, we are doing this here.

    # check if this student is already a member of the Yammer group corresponding to this course
    # if not, add them
    if not is_group_member(course, token):
        add_to_group(course, token)

    # now we can display the group feed
    network = token['network_name']
    feed_id = course.yammer_group_id # Yammer feed id is the same as the group id

    context = {
            'course': course,
            'course_id': course.id.to_deprecated_string(),
            'network': network,
            'feed_id': feed_id
        }

    return render_to_response('yammer/index.html', context)

# Check if user is member of Yammer group
def is_group_member(course, token):
    users_response = requests.get(
        yammer_api + 'users/in_group/' + course.yammer_group_id + '.json',
        headers={'Authorization': 'Bearer ' + token['token']})

    users = json.loads(users_response.content)["users"]

    found = False
    for user in users:
        if user['id'] == token['user_id']:
            return True

    return False

# add user to Yammer group
def add_to_group(course, token):
    add_response = requests.post(
        yammer_api + 'group_memberships.json?group_id=' + course.yammer_group_id,
        headers={'Authorization': 'Bearer ' + token['token']})

