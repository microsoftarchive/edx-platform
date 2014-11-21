"""
Contains all signal definitions milestones app listen to
"""
from django.dispatch import Signal

course_deleted = Signal(providing_args=["course_key"])  # pylint: disable=C0103
