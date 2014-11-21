"""
Helper methods for milestones api calls.
"""

from collections import defaultdict
from opaque_keys.edx.keys import CourseKey
from milestones.api import (
    get_course_milestones,
    get_courses_milestones,
    get_user_milestones,
    add_milestone,
    add_course_milestone,
    remove_course_milestone,
)


def get_prerequisite_course_key(course_key):
    """
    Retrieves pre_requisite_course_key for a course from milestones app
    """
    pre_requisite_course_key = None
    course_milestones = get_course_milestones(course_key=course_key, relationship="requires")
    if course_milestones:
        pre_requisite_course_key = course_milestones[0]['namespace']
    return pre_requisite_course_key


def add_prerequisite_course(course_key, prerequisite_course_key):
    """
    adds pre-requisite course milestone to a course
    """
    # add or get a milestone to be used as requirement
    requirement_milestone = add_milestone({
        'name': 'Course {} requires {}'.format(unicode(course_key), unicode(prerequisite_course_key)),
        'namespace': unicode(prerequisite_course_key),
        'description': '',
    })
    add_course_milestone(course_key, 'requires', requirement_milestone)

    # add or get a milestone to be used as fulfillment
    fulfillment_milestone = add_milestone({
        'name': 'Course {} fulfills {}'.format(unicode(prerequisite_course_key), unicode(course_key)),
        'namespace': unicode(course_key),
        'description': '',
    })
    add_course_milestone(prerequisite_course_key, 'fulfills', fulfillment_milestone)


def remove_prerequisite_course(course_key, milestone):
    """
    remove pre-requisite course milestone for a course
    """

    remove_course_milestone(
        course_key,
        milestone,
    )


def set_prerequisite_course(course_key, prerequisite_course_key_string):
    """
    add or update pre-requisite course milestone for a course
    """
    #remove any existing requirement milestones with this pre-requisite course as requirement
    course_milestones = get_course_milestones(course_key=course_key, relationship="requires")
    if course_milestones:
        for milestone in course_milestones:
            remove_prerequisite_course(course_key, milestone)

    # add milestones if pre-requisite course is selected
    if prerequisite_course_key_string:
        prerequisite_course_key = CourseKey.from_string(prerequisite_course_key_string)
        add_prerequisite_course(course_key, prerequisite_course_key)


def get_pre_requisite_courses(course_ids):
    """
    It would fetch pre-requisite courses for a list of courses

    Returns a dict with keys are set to course id and values are set to pre-requisite course keys .i.e.
    {
        "org/DemoX/2014_T2": {"milestone_id": "1", "prc_id": "org/cs23/2014_T2"}
    }
    """
    courses_dict = defaultdict(dict)
    milestones = get_courses_milestones(course_ids, relationship="requires")
    for milestone in milestones:
        pre_requisite_course_id = milestone['namespace']
        if pre_requisite_course_id:
            pre_requisite_course_key = CourseKey.from_string(pre_requisite_course_id)
            course_id = CourseKey.from_string(milestone['course_id'])
            courses_dict[course_id] = {
                "milestone_id": milestone['id'],
                "prc_id": pre_requisite_course_key
            }
    return courses_dict


def milestones_achieved_by_user(user):
    """
    It would fetch list of milestones completed by user
    """
    return get_user_milestones(user)


def get_prc_not_completed(user, enrolled_courses):
    """
    It would fetch list of prerequisite courses not completed by user
    """
    pre_requisite_courses = get_pre_requisite_courses(enrolled_courses)
    if pre_requisite_courses:
        completed_milestones = milestones_achieved_by_user({'id': user.id})
        completed_milestone_ids = [milestone["id"] for milestone in completed_milestones]
        # remove those pre-requisite courses which are already completed by user
        for course_id, data in pre_requisite_courses.items():
            if data["milestone_id"] in completed_milestone_ids:
                pre_requisite_courses.pop(course_id)

    return pre_requisite_courses
