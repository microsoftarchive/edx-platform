"""
Helper methods for milestones api calls.
"""

from opaque_keys.edx.keys import CourseKey
from milestones.api import get_course_milestones
from util.signals import course_prerequisite_course_added, course_prerequisite_course_removed


def get_prerequisite_course_key(course_key):
    """
    Retrieves pre_requisite_course_key for a course from milestones app
    """
    pre_requisite_course_key = None
    course_milestones = get_course_milestones(course_key=course_key, relationship="requires")
    if course_milestones:
        pre_requisite_course_key = course_milestones[0]['namespace']
    return pre_requisite_course_key


def add_prerequisite_course(course_key, prerequisite_course_key, milestone=None):
    """
    adds pre-requisite course milestone to a course
    """

    course_prerequisite_course_added.send(
        sender=add_prerequisite_course.__name__,
        course_key=course_key,
        milestone=milestone,
        prerequisite_course_key=prerequisite_course_key
    )


def remove_prerequisite_course(course_key, prerequisite_course_key, milestone=None):
    """
    remove pre-requisite course milestone from a course
    """

    course_prerequisite_course_removed.send(
        sender=remove_prerequisite_course.__name__,
        course_key=course_key,
        milestone=milestone,
        prerequisite_course_key=prerequisite_course_key
    )


def set_prerequisite_course(course_key, prerequisite_course_key_string):
    """
    add or update pre-requisite course milestone for a course
    """
    #remove any existing pre-requisite course milestones
    course_milestones = get_course_milestones(course_key=course_key, relationship="requires")
    if course_milestones:
        for milestone in course_milestones:
            prerequisite_course_key = CourseKey.from_string(milestone['namespace'])
            remove_prerequisite_course(course_key, prerequisite_course_key, milestone=None)

    # add milestones if pre-requisite course is selected
    if prerequisite_course_key_string:
        prerequisite_course_key = CourseKey.from_string(prerequisite_course_key_string)
        add_prerequisite_course(course_key, prerequisite_course_key, milestone=None)
