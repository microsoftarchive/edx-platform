"""
Acceptance tests for Studio's Settings Details pages
"""
from acceptance.tests.studio.base_studio_test import StudioCourseTest
from nose.tools import set_trace
from ...fixtures.course import CourseFixture
from ...pages.studio.settings import SettingsPage


class SettingsMilestonesTest(StudioCourseTest):
    """
    Tests for milestones feature in Studio's settings tab
    """
    def setUp(self):
        super(SettingsMilestonesTest, self).setUp(is_staff=True)
        self.settings_detail = SettingsPage(
            self.browser,
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run']
        )

        # Before every test, make sure to visit the page first
        self.settings_detail.visit()
        self.assertTrue(self.settings_detail.is_browser_on_page())

    # def test_page_has_prerequisite_field(self):
    #     """
    #     Test to make sure page has pre-requisite course field if milestones app is enabled.
    #     """
    #
    #     self.assertTrue(self.settings_detail.pre_requisite_course.present)

    def test_prerequisite_course_save_successfully(self):
        """
        Test to make sure pre-requisite course field successfully saving the changes.
        """
        c_f = CourseFixture(
            'test_org1',
            self.course_info['number'],
            self.course_info['run'],
            self.course_info['display_name']
        )
        c_f.install()

        set_trace()
        # self.settings_detail.select_pre_requisite_course_from_drop_down(index=1)
        # self.assertTrue(self.settings_detail.save_changes_button.present)
        #
        # # # now trigger the save changes button.
        # self.settings_detail.trigger_save_changes_button();
        # self.assertTrue('Your changes have been saved.' in self.settings_detail.browser.page_source)
        # self.settings_detail.refresh_page();
        # self.assertTrue(self.settings_detail.is_pre_requisite_course_selected())
        # set_trace()
        #
        #
        # # now reset/update the pre requisite course
        # self.settings_detail.select_pre_requisite_course_from_drop_down(index=0)
        # self.assertTrue(self.settings_detail.save_changes_button.present)
        #
        #
        # # # now trigger the save changes button to update the pre requisite course selection.
        # self.settings_detail.trigger_save_changes_button();
        # self.assertTrue('Your changes have been saved.' in self.settings_detail.browser.page_source)
        # self.assertFalse(self.settings_detail.is_pre_requisite_course_selected())


