"""
Tests related to the cohorting feature.
"""
from uuid import uuid4

from mixins import BaseDiscussionMixin
from ...pages.lms.auto_auth import AutoAuthPage
from ..helpers import UniqueCourseTest
from ...fixtures.course import CourseFixture
from ...pages.lms.discussion import DiscussionTabSingleThreadPage

from nose.plugins.attrib import attr


class CohortedDiscussionTestMixin(BaseDiscussionMixin):
    """
    Mixin for tests of cohorted discussions.
    """

    def setup_cohorts(self):
        """
        Sets up the course to use cohorting, and installs a default "Mock Cohort" cohort.
        """
        self.course_fixture._update_xblock(self.course_fixture._course_location, {
            "metadata": {
                u"cohort_config": {
                    "auto_cohort_groups": [],
                    "auto_cohort": False,
                    "cohorted_discussions": [
                        "mock-thread-id"
                    ],
                    "cohorted": True
                },
            },
        })
        self.cohort_1_name = "Cohort Group 1"
        self.cohort_1_id = self.add_cohort(self.cohort_1_name)

    def test_cohort_visibility_label(self):
        self.setup_thread(1, group_id=self.cohort_1_id)
        self.assertEquals(
            self.thread_page.get_group_visibility_label(),
            "This post visible only to {}.".format(self.cohort_1_name)
        )

    # def test_obsolete_cohort_visibility_label(self):
    #     self.setup_thread(1, group_id=999)
    #     self.assertEquals(self.thread_page.get_group_visibility_label(), "This post no longer visible to students.")


@attr('shard_1')
class CohortedDiscussionTabSingleThreadTest(UniqueCourseTest, CohortedDiscussionTestMixin):
    """
    Tests for the discussion page displaying a single thread
    """

    def setUp(self):
        super(CohortedDiscussionTabSingleThreadTest, self).setUp()
        self.discussion_id = "test_discussion_{}".format(uuid4().hex)

        # Create a course to register for
        self.course_fixture = CourseFixture(**self.course_info).install()
        self.setup_cohorts()
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def setup_thread_page(self, thread_id):
        self.thread_page = DiscussionTabSingleThreadPage(self.browser, self.course_id, thread_id)  # pylint:disable=W0201
        self.thread_page.visit()