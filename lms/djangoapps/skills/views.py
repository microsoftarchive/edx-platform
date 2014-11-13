
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django_future.csrf import ensure_csrf_cookie

from edxmako.shortcuts import render_to_response
from util.views import ensure_valid_course_key

from courseware.courses import get_course_with_access
from courseware.views import fetch_reverify_banner_info

from opaque_keys.edx.locations import SlashSeparatedCourseKey

from skills.client import get_skills_and_values


@login_required
@ensure_csrf_cookie
@ensure_valid_course_key
def index(request, course_id):
    user = request.user
    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    course = get_course_with_access(user, 'load', course_key, depth=None, check_if_enrolled=True)

    skills = get_skills_and_values(course, user)

    context = {
        'course': course,
        'student': user,
        'reverifications': fetch_reverify_banner_info(request, course_key),
        'skills': skills,
    }

    return render_to_response('courseware/skills/index.html', context)
