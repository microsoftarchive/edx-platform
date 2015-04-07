"""
This file contains implementation override of SearchFilterGenerator which will allow
    * Filter by all courses in which the user is enrolled in
"""
from datetime import datetime

from student.models import CourseEnrollment
from opaque_keys.edx.keys import CourseKey

from search.filter_generator import SearchFilterGenerator
from search.utils import DateRange
from openedx.core.djangoapps.course_groups.cohorts import get_cohort
from openedx.core.djangoapps.course_groups.models import CourseUserGroupPartitionGroup


class LmsSearchFilterGenerator(SearchFilterGenerator):
    """ SearchFilterGenerator for LMS Search """

    def filter_dictionary(self, **kwargs):
        """ base implementation which filters via start_date """
        filter_dictionary = {"start_date": DateRange(None, datetime.utcnow())}
        if 'user' in kwargs and 'course_id' in kwargs:
            try:
                course_key = CourseKey.from_string(kwargs['course_id'])
            except InvalidKeyError:
                course_key = SlashSeparatedCourseKey.from_deprecated_string(kwargs['course_id'])
            cohort = get_cohort(kwargs['user'], course_key, assign=False)
            partition_group = None
            try:
                partition_group = CourseUserGroupPartitionGroup.objects.get(course_user_group=cohort)
            except CourseUserGroupPartitionGroup.DoesNotExist:
                pass
            if partition_group:
                partition_group = partition_group.group_id
        filter_dictionary['content_groups'] = unicode(partition_group)
        return filter_dictionary

    def field_dictionary(self, **kwargs):
        """ add course if provided otherwise add courses in which the user is enrolled in """
        field_dictionary = super(LmsSearchFilterGenerator, self).field_dictionary(**kwargs)
        if 'user' not in kwargs or not kwargs['user']:
            field_dictionary['course'] = []
        elif 'course_id' not in kwargs or not kwargs['course_id']:
            user_enrollments = CourseEnrollment.enrollments_for_user(kwargs['user'])
            field_dictionary['course'] = [unicode(enrollment.course_id) for enrollment in user_enrollments]

        return field_dictionary
