"""
Courses API v0 URI specification
The order of the URIs really matters here, due to the slash characters present in the identifiers
"""
from django.conf import settings
from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns

from course_structure_api.v0 import views


CONTENT_ID_PATTERN = settings.USAGE_ID_PATTERN.replace('usage_id', 'content_id')
COURSE_ID_PATTERN = settings.COURSE_ID_PATTERN

# pylint: disable=invalid-name
course_patterns = patterns(
    '',
    url(r'^$', views.CourseDetail.as_view(), name='detail'),
    url(r'^grading_policy/$', views.CourseGradingPolicy.as_view(), name='grading_policy'),
    url(r'^structure/$', views.CourseStructure.as_view(), name='structure'),
)

urlpatterns = patterns(
    '',
    url(r'^$', views.CourseList.as_view(), name='list'),
    url(r'^{}/'.format(COURSE_ID_PATTERN), include(course_patterns))
)

urlpatterns = format_suffix_patterns(urlpatterns)
