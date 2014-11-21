"""
Contains all signal definitions milestones app listen
"""
from django.dispatch import Signal

course_completed = Signal(providing_args=["course_key", "student"])  # pylint: disable=C0103
course_deleted = Signal(providing_args=["course_key"])  # pylint: disable=C0103
course_entrance_exam_added = Signal(providing_args=["course_key", "content_key", "milestone"])  # pylint: disable=C0103
course_prerequisite_course_added = Signal(providing_args=["course_key", "prerequisite_course_key", "milestone"])  # pylint: disable=C0103
course_prerequisite_course_removed = Signal(providing_args=["course_key", "prerequisite_course_key", "milestone"])  # pylint: disable=C0103
