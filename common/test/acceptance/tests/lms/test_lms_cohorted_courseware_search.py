"""
Test courseware search
"""
import os
import json

from ..helpers import create_user_partition_json
from ...pages.common.logout import LogoutPage
from ...pages.studio.utils import add_html_component, click_css, type_in_codemirror
from ...pages.studio.overview import CourseOutlinePage
from ...pages.studio.container import ContainerPage
from ...pages.lms.courseware_search import CoursewareSearchPage
from ...fixtures.course import CourseFixture, XBlockFixtureDesc

from nose.plugins.attrib import attr

from ..studio.base_studio_test import ContainerBase

from ...pages.studio.settings_group_configurations import GroupConfigurationsPage
from ...pages.studio.auto_auth import AutoAuthPage as StudioAutoAuthPage
from ...fixtures import LMS_BASE_URL
from ...pages.studio.component_editor import ComponentVisibilityEditorView
from ...pages.lms.instructor_dashboard import InstructorDashboardPage
from ...pages.lms.courseware import CoursewarePage
from ...pages.lms.auto_auth import AutoAuthPage as LmsAutoAuthPage
from ...tests.lms.test_lms_user_preview import verify_expected_problem_visibility

from bok_choy.promise import EmptyPromise

@attr('shard_1')
class CoursewareSearchCohortTest(ContainerBase):
    """
    Test courseware search.
    """
    USERNAME = 'STUDENT_TESTER'
    EMAIL = 'student101@example.com'

    STAFF_USERNAME = "STAFF_TESTER"
    STAFF_EMAIL = "staff101@example.com"

    HTML_CONTENT = """
            Someday I'll wish upon a star
            And wake up where the clouds are far
            Behind me.
            Where troubles melt like lemon drops
            Away above the chimney tops
            That's where you'll find me.
        """
    SEARCH_STRING = "chimney"
    EDITED_CHAPTER_NAME = "Section 2 - edited"
    EDITED_SEARCH_STRING = "edited"

    TEST_INDEX_FILENAME = "test_root/index_file.dat"

    def setUp(self, is_staff=True):
        """
        Create search page and course content to search
        """
        # create test file in which index for this test will live
        with open(self.TEST_INDEX_FILENAME, "w+") as index_file:
            json.dump({}, index_file)

        super(CoursewareSearchCohortTest, self).setUp(is_staff=is_staff)
        self.staff_user = self.user

        self.course_outline = CourseOutlinePage(
            self.browser,
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run']
        )

        self.content_group_a = "Content Group A"
        self.content_group_b = "Content Group B"

        # Create a student who will be in "Cohort A"
        self.cohort_a_student_username = "cohort_a_student"
        self.cohort_a_student_email = "cohort_a_student@example.com"
        StudioAutoAuthPage(
            self.browser, username=self.cohort_a_student_username, email=self.cohort_a_student_email, no_login=True
        ).visit()

        # Create a student who will be in "Cohort B"
        self.cohort_b_student_username = "cohort_b_student"
        self.cohort_b_student_email = "cohort_b_student@example.com"
        StudioAutoAuthPage(
            self.browser, username=self.cohort_b_student_username, email=self.cohort_b_student_email, no_login=True
        ).visit()

        # Create a student who will end up in the default cohort group
        self.cohort_default_student_username = "cohort_default_student"
        self.cohort_default_student_email = "cohort_default_student@example.com"
        StudioAutoAuthPage(
            self.browser, username=self.cohort_default_student_username,
            email=self.cohort_default_student_email, no_login=True
        ).visit()

        # Start logged in as the staff user.
        StudioAutoAuthPage(
            self.browser, username=self.staff_user["username"], email=self.staff_user["email"]
        ).visit()

        self.courseware_search_page = CoursewareSearchPage(self.browser, self.course_id)

        self.course_outline = self.outline

    def tearDown(self):
        os.remove(self.TEST_INDEX_FILENAME)

    def _auto_auth(self, username, email, staff):
        """
        Logout and login with given credentials.
        """
        LogoutPage(self.browser).visit()
        StudioAutoAuthPage(self.browser, username=username, email=email,
                     course_id=self.course_id, staff=staff).visit()

    def _studio_add_content(self, section_index):
        """
        Add content on studio course page under specified section
        """

        # create a unit in course outline
        self.course_outline.visit()
        subsection = self.course_outline.section_at(section_index).subsection_at(0)
        subsection.expand_subsection()
        subsection.add_unit()

        # got to unit and create an HTML component and save (not publish)
        unit_page = ContainerPage(self.browser, None)
        unit_page.wait_for_page()
        add_html_component(unit_page, 0)
        unit_page.wait_for_element_presence('.edit-button', 'Edit button is visible')
        click_css(unit_page, '.edit-button', 0, require_notification=False)
        unit_page.wait_for_element_visibility('.modal-editor', 'Modal editor is visible')
        type_in_codemirror(unit_page, 0, self.HTML_CONTENT)
        click_css(unit_page, '.action-save', 0)

    def _studio_publish_content(self, section_index):
        """
        Publish content on studio course page under specified section
        """
        self.course_outline.visit()
        subsection = self.course_outline.section_at(section_index).subsection_at(0)
        subsection.expand_subsection()
        unit = subsection.unit_at(0)
        unit.publish()

    def populate_course_fixture(self, course_fixture):
        """
        Populate the children of the test course fixture.
        """
        self.group_a_problem = 'GROUP A CONTENT'
        self.group_b_problem = 'GROUP B CONTENT'
        self.group_a_and_b_problem = 'GROUP A AND B CONTENT'
        self.visible_to_all_problem = 'VISIBLE TO ALL CONTENT'

        course_fixture.add_children(
            XBlockFixtureDesc('chapter', 'Section 1').add_children(
                XBlockFixtureDesc('sequential', 'Subsection 1')
            )
        ).add_children(
            XBlockFixtureDesc('chapter', 'Section 2').add_children(
                XBlockFixtureDesc('sequential', 'Subsection 2')
            )
        ).add_children(
            XBlockFixtureDesc('chapter', 'Test Section').add_children(
                XBlockFixtureDesc('sequential', 'Test Subsection').add_children(
                    XBlockFixtureDesc('vertical', 'Test Unit').add_children(
                        XBlockFixtureDesc('problem', self.group_a_problem, data='<problem></problem>'),
                        XBlockFixtureDesc('problem', self.group_b_problem, data='<problem></problem>'),
                        XBlockFixtureDesc('problem', self.group_a_and_b_problem, data='<problem></problem>'),
                        XBlockFixtureDesc('problem', self.visible_to_all_problem, data='<problem></problem>')
                    )
                )
            )
        )

    def enable_cohorting(self, course_fixture):
        """
        Enables cohorting for the current course.
        """
        url = LMS_BASE_URL + "/courses/" + course_fixture._course_key + '/cohorts/settings'  # pylint: disable=protected-access
        data = json.dumps({'is_cohorted': True})
        response = course_fixture.session.patch(url, data=data, headers=course_fixture.headers)
        self.assertTrue(response.ok, "Failed to enable cohorts")

    def create_content_groups(self):
        """
        Creates two content groups in Studio Group Configurations Settings.
        """
        group_configurations_page = GroupConfigurationsPage(
            self.browser,
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run']
        )
        group_configurations_page.visit()

        group_configurations_page.create_first_content_group()
        config = group_configurations_page.content_groups[0]
        config.name = self.content_group_a
        config.save()

        group_configurations_page.add_content_group()
        config = group_configurations_page.content_groups[1]
        config.name = self.content_group_b
        config.save()

    def link_problems_to_content_groups_and_publish(self):
        """
        Updates 3 of the 4 existing problems to limit their visibility by content group.
        Publishes the modified units.
        """
        container_page = self.go_to_unit_page()

        def set_visibility(problem_index, content_group, second_content_group=None):
            problem = container_page.xblocks[problem_index]
            problem.edit_visibility()
            if second_content_group:
                ComponentVisibilityEditorView(self.browser, problem.locator).select_option(
                    second_content_group, save=False
                )
            ComponentVisibilityEditorView(self.browser, problem.locator).select_option(content_group)

        set_visibility(1, self.content_group_a)
        set_visibility(2, self.content_group_b)
        set_visibility(3, self.content_group_a, self.content_group_b)

        container_page.publish_action.click()

    def create_cohorts_and_assign_students(self):
        """
        Adds 2 manual cohorts, linked to content groups, to the course.
        Each cohort is assigned one student.
        """
        instructor_dashboard_page = InstructorDashboardPage(self.browser, self.course_id)
        instructor_dashboard_page.visit()
        cohort_management_page = instructor_dashboard_page.select_cohort_management()

        def add_cohort_with_student(cohort_name, content_group, student):
            cohort_management_page.add_cohort(cohort_name, content_group=content_group)
            # After adding the cohort, it should automatically be selected
            EmptyPromise(
                lambda: cohort_name == cohort_management_page.get_selected_cohort(), "Waiting for new cohort"
            ).fulfill()
            cohort_management_page.add_students_to_selected_cohort([student])

        add_cohort_with_student("Cohort A", self.content_group_a, self.cohort_a_student_username)
        add_cohort_with_student("Cohort B", self.content_group_b, self.cohort_b_student_username)

    def view_cohorted_content_as_different_users(self):
        """
        View content as staff, student in Cohort A, student in Cohort B, and student in Default Cohort.
        """
        courseware_page = CoursewarePage(self.browser, self.course_id)

        def login_and_verify_visible_problems(username, email, expected_problems):
            LmsAutoAuthPage(
                self.browser, username=username, email=email, course_id=self.course_id
            ).visit()
            courseware_page.visit()
            verify_expected_problem_visibility(self, courseware_page, expected_problems)

        login_and_verify_visible_problems(
            self.staff_user["username"], self.staff_user["email"],
            [self.group_a_problem, self.group_b_problem, self.group_a_and_b_problem, self.visible_to_all_problem]
        )

        login_and_verify_visible_problems(
            self.cohort_a_student_username, self.cohort_a_student_email,
            [self.group_a_problem, self.group_a_and_b_problem, self.visible_to_all_problem]
        )

        login_and_verify_visible_problems(
            self.cohort_b_student_username, self.cohort_b_student_email,
            [self.group_b_problem, self.group_a_and_b_problem, self.visible_to_all_problem]
        )

        login_and_verify_visible_problems(
            self.cohort_default_student_username, self.cohort_default_student_email,
            [self.visible_to_all_problem]
        )


    def test_page_existence(self):
        """
        Make sure that the page is accessible.
        """
        self._auto_auth(self.USERNAME, self.EMAIL, False)
        self.courseware_search_page.visit()

    def test_cohorted_courseware_search(self):

        # Create content in studio without publishing.
        self._auto_auth(self.STAFF_USERNAME, self.STAFF_EMAIL, True)
        self._studio_add_content(0)

        # Publish in studio to trigger indexing.
        self._auto_auth(self.STAFF_USERNAME, self.STAFF_EMAIL, True)
        self._studio_publish_content(0)
        self.browser.save_screenshot('test_shot.jpg')

        # Do the search again, this time we expect results.
        self._auto_auth(self.USERNAME, self.EMAIL, False)
        self.courseware_search_page.visit()
        self.browser.save_screenshot('test_shot2.jpg')
        self.courseware_search_page.search_for_term(self.SEARCH_STRING)
        self.browser.save_screenshot('test_shot3.jpg')
        assert self.SEARCH_STRING in self.courseware_search_page.search_results.html[0]

        # Enable Cohorting
        self.enable_cohorting(self.course_fixture)
        self.create_content_groups()
        self.link_problems_to_content_groups_and_publish()
        self.create_cohorts_and_assign_students()
        self.view_cohorted_content_as_different_users()
