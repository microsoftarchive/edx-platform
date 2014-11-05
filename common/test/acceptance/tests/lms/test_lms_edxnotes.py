from uuid import uuid4
from datetime import datetime
from ..helpers import UniqueCourseTest
from ...fixtures.course import CourseFixture, XBlockFixtureDesc
from ...pages.lms.auto_auth import AutoAuthPage
from ...pages.lms.course_nav import CourseNavPage
from ...pages.lms.courseware import CoursewarePage
from ...pages.lms.edxnotes import EdxNotesUnitPage, EdxNotesPage
from ...fixtures.edxnotes import EdxNotesFixture, Note, Range


class EdxNotesTestMixin(UniqueCourseTest):
    """
    Creates a course with initial data and contains useful helper methods.
    """
    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(EdxNotesTestMixin, self).setUp()
        self.courseware_page = CoursewarePage(self.browser, self.course_id)
        self.course_nav = CourseNavPage(self.browser)
        self.note_unit_page = EdxNotesUnitPage(self.browser, self.course_id)
        self.notes_page = EdxNotesPage(self.browser, self.course_id)

        self.username = str(uuid4().hex)[:5]
        self.email = "{}@email.com".format(self.username)

        self.selector = "annotate-id"
        self.edxnotes_fixture = EdxNotesFixture()
        self.course_fixture = CourseFixture(
            self.course_info["org"], self.course_info["number"],
            self.course_info["run"], self.course_info["display_name"]
        )

        self.course_fixture.add_advanced_settings({
            u"edxnotes": {u"value": True}
        })

        self.course_fixture.add_children(
            XBlockFixtureDesc("chapter", "Test Section").add_children(
                XBlockFixtureDesc("sequential", "Test Subsection").add_children(
                    XBlockFixtureDesc("vertical", "Test Vertical").add_children(
                        XBlockFixtureDesc(
                            "html",
                            "Test HTML 1",
                            data="""
                                <p><span class="{0}">Annotate</span> this text!</p>
                                <p>Annotate this <span class="{0}">text</span></p>
                            """.format(self.selector)
                        ),
                        XBlockFixtureDesc(
                            "html",
                            "Test HTML 2",
                            data="""<p>Annotate <span class="{}">this text!</span></p>""".format(self.selector)
                        ),
                    ),
                    XBlockFixtureDesc(
                        "html",
                        "Test HTML 3",
                        data="""<p><span class="{}">Annotate this text!</span></p>""".format(self.selector)
                    ),
                ),
            )).install()

        AutoAuthPage(self.browser, username=self.username, email=self.email, course_id=self.course_id).visit()

    def tearDown(self):
        self.edxnotes_fixture.cleanup()

    def _add_notes(self):
        xblocks = self.course_fixture.get_nested_xblocks(category="html")
        notes_list = []
        for index, xblock in enumerate(xblocks):
            notes_list.append(
                Note(
                    user=self.username,
                    usage_id=xblock.locator,
                    course_id=self.course_fixture._course_key,
                    ranges=[Range(startOffset=index, endOffset=index + 5)]
                )
            )

        self.edxnotes_fixture.create_notes(notes_list)
        self.edxnotes_fixture.install()


class EdxNotesDefaultInteractionsTest(EdxNotesTestMixin):
    """
    Tests for creation, editing, deleting annotations inside annotatable components in LMS.
    """
    def create_notes(self, components, offset=0):
        self.assertGreater(len(components), 0)
        index = offset
        for component in components:
            for note in component.create_note(".annotate-id"):
                note.text = "TEST TEXT {}".format(index)
                index += 1

    def edit_notes(self, components, offset=0):
        self.assertGreater(len(components), 0)
        index = offset
        for component in components:
            self.assertGreater(len(component.notes), 0)
            for note in component.edit_note():
                note.text = "TEST TEXT {}".format(index)
                index += 1

    def remove_notes(self, components):
        self.assertGreater(len(components), 0)
        for component in components:
            self.assertGreater(len(component.notes), 0)
            component.remove_note()

    def assert_notes_are_removed(self, components):
        for component in components:
            self.assertEqual(0, len(component.notes))

    def assert_text_in_notes(self, components, offset=0):
        index = offset
        for component in components:
            actual = [note.text for note in component.notes]
            expected = ["TEST TEXT {}".format(i + index) for i in xrange(len(actual))]
            index += len(actual)
            self.assertItemsEqual(expected, actual)

    def test_can_create_notes(self):
        """
        Scenario: User can create notes.
        Given I have a course with 3 annotatable components
        And I open the unit with 2 annotatable components
        When I add 2 notes for the first component and 1 note for the second
        Then I see that notes were correctly created
        When I change sequential position to "2"
        And I add note for the annotatable component on the page
        Then I see that note was correctly created
        When I refresh the page
        Then I see that note was correctly stored
        When I change sequential position to "1"
        Then I see that notes were correctly stored on the page
        """
        self.note_unit_page.visit()

        components = self.note_unit_page.components
        self.create_notes(components)
        self.assert_text_in_notes(components)
        offset = len(self.note_unit_page.notes)

        self.course_nav.go_to_sequential_position(2)
        components = self.note_unit_page.components
        self.create_notes(components, offset)
        self.assert_text_in_notes(components, offset)

        components = self.note_unit_page.refresh()
        self.assert_text_in_notes(components, offset)

        self.course_nav.go_to_sequential_position(1)
        components = self.note_unit_page.components
        self.assert_text_in_notes(components)

    def test_can_edit_notes(self):
        """
        Scenario: User can edit notes.
        Given I have a course with 3 components with notes
        And I open the unit with 2 annotatable components
        When I change text in the notes
        Then I see that notes were correctly changed
        When I change sequential position to "2"
        And I change the note on the page
        Then I see that note was correctly changed
        When I refresh the page
        Then I see that edited note was correctly stored
        When I change sequential position to "1"
        Then I see that edited notes were correctly stored on the page
        """
        self._add_notes()
        self.note_unit_page.visit()

        components = self.note_unit_page.components
        self.edit_notes(components)
        self.assert_text_in_notes(components)
        offset = len(self.note_unit_page.notes)

        self.course_nav.go_to_sequential_position(2)
        components = self.note_unit_page.components
        self.edit_notes(components, offset)
        self.assert_text_in_notes(components, offset)

        components = self.note_unit_page.refresh()
        self.assert_text_in_notes(components, offset)

        self.course_nav.go_to_sequential_position(1)
        components = self.note_unit_page.components
        self.assert_text_in_notes(components)

    def test_can_delete_notes(self):
        """
        Scenario: User can delete notes.
        Given I have a course with 3 components with notes
        And I open the unit with 2 annotatable components
        When I remove all notes on the page
        Then I do not see any notes on the page
        When I change sequential position to "2"
        And I remove all notes on the page
        Then I do not see any notes on the page
        When I refresh the page
        Then I do not see any notes on the page
        When I change sequential position to "1"
        Then I do not see any notes on the page
        """
        self._add_notes()
        self.note_unit_page.visit()

        components = self.note_unit_page.components
        self.remove_notes(components)
        self.assert_notes_are_removed(components)

        self.course_nav.go_to_sequential_position(2)
        components = self.note_unit_page.components
        self.remove_notes(components)
        self.assert_notes_are_removed(components)

        components = self.note_unit_page.refresh()
        self.assert_notes_are_removed(components)

        self.course_nav.go_to_sequential_position(1)
        components = self.note_unit_page.components
        self.assert_notes_are_removed(components)


class EdxNotesToggleSingleNoteTest(EdxNotesTestMixin):
    """
    Tests for toggling single annotation.
    """

    def setUp(self):
        super(EdxNotesToggleSingleNoteTest, self).setUp()
        self._add_notes()
        self.note_page.visit()

    def test_can_toggle_by_clicking_on_highlighted_text(self):
        """
        Scenario: User can toggle a single note by clicking on highlighted text.
        Given I have a course with components with notes
        When I click on highlighted text
        And I move mouse out of the note
        Then I see that the note is still shown
        When I click outside the note
        Then I see the the note is closed
        """
        note = self.note_page.notes[0]

        note.click_on_highlight()
        self.note_page.move_mouse_to('body')
        self.assertTrue(note.is_visible)
        self.note_page.click('body')
        self.assertFalse(note.is_visible)

    def test_can_toggle_by_clicking_on_the_note(self):
        """
        Scenario: User can toggle a single note by clicking on the note.
        Given I have a course with components with notes
        When I click on the note
        And I move mouse out of the note
        Then I see that the note is still shown
        When I click outside the note
        Then I see the the note is closed
        """
        note = self.note_page.notes[0]

        note.show().click_on_viewer()
        self.note_page.move_mouse_to('body')
        self.assertTrue(note.is_visible)
        self.note_page.click('body')
        self.assertFalse(note.is_visible)

    def test_interaction_between_notes(self):
        """
        Scenario: Interactions between notes works well.
        Given I have a course with components with notes
        When I click on highlighted text in the first component
        And I move mouse out of the note
        Then I see that the note is still shown
        When I click on highlighted text in the second component
        Then I do not see any notes
        When I click again on highlighted text in the second component
        Then I see appropriate note
        """
        note_1 = self.note_page.notes[0]
        note_2 = self.note_page.notes[1]

        note_1.click_on_highlight()
        self.note_page.move_mouse_to('body')
        self.assertTrue(note_1.is_visible)

        note_2.click_on_highlight()
        self.assertFalse(note_1.is_visible)
        self.assertFalse(note_2.is_visible)

        note_2.click_on_highlight()
        self.assertTrue(note_2.is_visible)
>>>>>>> TNL-660: Toggle single note visibility.
