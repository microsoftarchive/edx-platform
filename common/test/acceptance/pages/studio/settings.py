"""
Course Schedule and Details Settings page.
"""

from .course_page import CoursePage
from selenium.webdriver.support.ui import Select
from nose.tools import set_trace

PRE_REQUISITE_COURSE_SELECTOR = "pre-requisite-course"
SAVE_BUTTON_SELECTOR = ".button.action-primary.action-save"

class SettingsPage(CoursePage):
    """
    Course Schedule and Details Settings page.
    """

    url_path = "settings/details"

    def is_browser_on_page(self):
        return self.q(css='body.view-settings').present

    @property
    def pre_requisite_course(self):
        """
        Returns the pre-requisite course drop down field.
        """
        return self.q(css='#pre-requisite-course')

    @property
    def save_changes_button(self):
        """
        Returns the pre-requisite course drop down field.
        """
        return self.q(css='a.button.action-primary.action-save')

    def trigger_save_changes_button(self):
        """
        Trigger the save changes button.
        """
        self.q(css=SAVE_BUTTON_SELECTOR).click()
        self.wait_for_ajax()

    def select_pre_requisite_course_from_drop_down(self, index):
        """
        Select the course from drop down at given index.
        """
        select = Select(self.browser.find_element_by_id("{selector}".format(selector=PRE_REQUISITE_COURSE_SELECTOR)))
        select.select_by_index(index)

    def is_pre_requisite_course_selected(self):
        """
        Check either a course is selected in pre requisite courses drop down
        """
        select = Select(self.browser.find_element_by_id("{selector}".format(selector=PRE_REQUISITE_COURSE_SELECTOR)))
        return (select.first_selected_option.is_selected() and select.first_selected_option.text != 'None')

    def refresh_page(self):
        """
        Reload the page.
        """
        self.browser.refresh()

