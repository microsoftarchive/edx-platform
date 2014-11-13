import datetime
import functools
import json
import logging
import pytz

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_control
from django_future.csrf import ensure_csrf_cookie

from courseware.courses import get_course_by_id
from courseware.field_overrides import disable_overrides
from edxmako.shortcuts import render_to_response
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from student.roles import CoursePocCoachRole

from .models import PersonalOnlineCourse
from .overrides import override_field_for_poc, get_override_for_poc

log = logging.getLogger(__name__)
today = datetime.datetime.today  # for patching in tests


def coach_dashboard(view):
    """
    View decorator which enforces that the user have the POC coach role on the
    given course and goes ahead and translates the course_id from the Django
    route into a course object.
    """
    @functools.wraps(view)
    def wrapper(request, course_id):
        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
        role = CoursePocCoachRole(course_key)
        if not role.has_user(request.user):
            return HttpResponseForbidden(
                _('You must be a POC Coach to access this view.'))
        course = get_course_by_id(course_key, depth=None)
        return view(request, course)
    return wrapper


@ensure_csrf_cookie
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@coach_dashboard
def dashboard(request, course):
    """
    Display the POC Coach Dashboard.
    """
    poc = get_poc_for_coach(course, request.user)
    schedule = get_poc_schedule(course, poc)
    context = {
        'course': course,
        'poc': poc,
        'schedule': json.dumps(schedule, indent=4),
        'save_url': reverse('save_poc', kwargs={'course_id': course.id}),
    }
    if not poc:
        context['create_poc_url'] = reverse(
            'create_poc', kwargs={'course_id': course.id})
    return render_to_response('pocs/coach_dashboard.html', context)


@ensure_csrf_cookie
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@coach_dashboard
def create_poc(request, course):
    """
    Create a new POC
    """
    name = request.POST.get('name')
    poc = PersonalOnlineCourse(
        course_id=course.id,
        coach=request.user,
        display_name=name)
    poc.save()

    # Make sure start/due are overridden for entire course
    start = today().replace(tzinfo=pytz.UTC)
    override_field_for_poc(poc, course, 'start', start)
    override_field_for_poc(poc, course, 'due', None)

    # Hide anything that can appear in the course outline to start out with
    for chapter in course.get_children():
        override_field_for_poc(poc, chapter, 'start', start)
        override_field_for_poc(poc, chapter, 'hidden', True)
        for sequential in chapter.get_children():
            override_field_for_poc(poc, sequential, 'hidden', True)
            for vertical in sequential.get_children():
                override_field_for_poc(poc, vertical, 'hidden', True)

    url = reverse('poc_coach_dashboard', kwargs={'course_id': course.id})
    return redirect(url)


@ensure_csrf_cookie
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@coach_dashboard
def save_poc(request, course):
    """
    Save changes to POC
    """
    poc = get_poc_for_coach(course, request.user)

    def override_fields(parent, data, earliest=None):
        blocks = {
            str(child.location): child
            for child in parent.get_children()}
        for unit in data:
            block = blocks[unit['location']]
            override_field_for_poc(poc, block, 'hidden', unit['hidden'])
            start = parse_date(unit['start'])
            if start:
                if not earliest or start < earliest:
                    earliest = start
                override_field_for_poc(poc, block, 'start', start)
            due = parse_date(unit['due'])
            if due:
                override_field_for_poc(poc, block, 'due', due)

            children = unit.get('children', None)
            if children:
                override_fields(block, children, earliest)
        return earliest

    earliest = override_fields(course, json.loads(request.body))
    if earliest:
        override_field_for_poc(poc, course, 'start', earliest)

    return HttpResponse(
        json.dumps(get_poc_schedule(course, poc)),
        content_type='application/json')


def parse_date(s):
    if s:
        try:
            date, time = s.split(' ')
            year, month, day = map(int, date.split('-'))
            hour, minute = map(int, time.split(':'))
            return datetime.datetime(
                year, month, day, hour, minute, tzinfo=pytz.UTC)
        except:
            log.warn("Unable to parse date: " + s)

    return None


def get_poc_for_coach(course, coach):
    """
    Looks to see if user is coach of a POC for this course.  Returns the POC or
    None.
    """
    try:
        return PersonalOnlineCourse.objects.get(
            course_id=course.id,
            coach=coach)
    except PersonalOnlineCourse.DoesNotExist:
        return None


def get_poc_schedule(course, poc):
    """
    """
    def visit(node, depth=1):
        for child in node.get_children():
            start = get_override_for_poc(poc, child, 'start', None)
            if start:
                start = str(start)[:-9]
            due = get_override_for_poc(poc, child, 'due', None)
            if due:
                due = str(due)[:-9]
            hidden = get_override_for_poc(poc, child, 'hidden', child.hidden)
            visited = {
                'location': str(child.location),
                'display_name': child.display_name,
                'category': child.category,
                'start': start,
                'due': due,
                'hidden': hidden,
            }
            if depth < 3:
                children = tuple(visit(child, depth + 1))
                if children:
                    visited['children'] = children
                    yield visited
            else:
                yield visited

    with disable_overrides():
        return tuple(visit(course))
