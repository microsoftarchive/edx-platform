"""
Run these tests @ Devstack:
    paver test_system -s lms --fasttest --verbose --test_id=lms/djangoapps/course_structure_api
"""
# pylint: disable=missing-docstring,invalid-name,maybe-no-member

from datetime import datetime

from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from oauth2_provider.tests.factories import AccessTokenFactory, ClientFactory
from opaque_keys.edx.locations import BlockUsageLocator
from xmodule.modulestore.tests.django_utils import TEST_DATA_MOCK_MODULESTORE, ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory

from courseware.tests.factories import GlobalStaffFactory, StaffFactory


TEST_SERVER_HOST = 'http://testserver'


class AuthMixin(object):
    def create_user_and_access_token(self):
        self.user = GlobalStaffFactory.create()
        self.oauth_client = ClientFactory.create()
        self.access_token = AccessTokenFactory.create(user=self.user, client=self.oauth_client).token


class CourseViewTestsMixin(AuthMixin):
    """
    Mixin for course view tests.
    """
    view = None

    def setUp(self):
        super(CourseViewTestsMixin, self).setUp()
        self.create_test_data()
        self.create_user_and_access_token()

    # pylint: disable=attribute-defined-outside-init
    def create_test_data(self):
        self.invalid_course_id = 'foo/bar/baz'
        self.course = CourseFactory.create(display_name='An Introduction to API Testing', raw_grader=[
            {
                "min_count": 24,
                "weight": 0.2,
                "type": "Homework",
                "drop_count": 0,
                "short_label": "HW"
            },
            {
                "min_count": 4,
                "weight": 0.8,
                "type": "Exam",
                "drop_count": 0,
                "short_label": "Exam"
            }
        ])
        self.course_id = unicode(self.course.id)

        sequential = ItemFactory.create(
            category="sequential",
            parent_location=self.course.location,
            display_name="Lesson 1",
            format="Homework",
            graded=True
        )

        ItemFactory.create(
            category="problem",
            parent_location=sequential.location,
            display_name="Problem 1",
            format="Homework"
        )

        self.empty_course = CourseFactory.create(
            start=datetime(2014, 6, 16, 14, 30),
            end=datetime(2015, 1, 16),
            org="MTD"
        )

    def build_absolute_url(self, path=None):
        """ Build absolute URL pointing to test server.
        :param path: Path to append to the URL
        """
        url = TEST_SERVER_HOST

        if path:
            url += path

        return url

    def assertValidResponseCourse(self, data, course):
        """ Determines if the given response data (dict) matches the specified course. """

        course_key = course.id
        self.assertEqual(data['id'], unicode(course_key))
        self.assertEqual(data['name'], course.display_name)
        self.assertEqual(data['course'], course_key.course)
        self.assertEqual(data['org'], course_key.org)
        self.assertEqual(data['run'], course_key.run)

        uri = self.build_absolute_url(
            reverse('course_structure_api_v0:detail', kwargs={'course_id': unicode(course_key)}))
        self.assertEqual(data['uri'], uri)

    def http_get(self, uri, **headers):
        """Submit an HTTP GET request"""

        default_headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + self.access_token
        }
        default_headers.update(headers)

        response = self.client.get(uri, content_type='application/json', follow=True, **default_headers)
        return response

    def test_not_authenticated(self):
        """
        Verify that access is denied to non-authenticated users.
        """
        raise NotImplementedError

    def test_not_authorized(self):
        """
        Verify that access is denied to non-authorized users.
        """
        raise NotImplementedError


class CourseDetailMixin(object):
    """
    Mixin for views utilizing only the course_id kwarg.
    """

    def test_get_invalid_course(self):
        """
        The view should return a 404 if the course ID is invalid.
        """
        response = self.http_get(reverse(self.view, kwargs={'course_id': self.invalid_course_id}))
        self.assertEqual(response.status_code, 404)

    def test_get(self):
        """
        The view should return a 200 if the course ID is invalid.
        """
        response = self.http_get(reverse(self.view, kwargs={'course_id': self.course_id}))
        self.assertEqual(response.status_code, 200)

        # Return the response so child classes do not have to repeat the request.
        return response

    def test_not_authenticated(self):
        # If debug mode is enabled, the view should always return data.
        with override_settings(DEBUG=True):
            response = self.http_get(reverse(self.view, kwargs={'course_id': self.course_id}), HTTP_AUTHORIZATION=None)
            self.assertEqual(response.status_code, 200)

        response = self.http_get(reverse(self.view, kwargs={'course_id': self.course_id}), HTTP_AUTHORIZATION=None)
        self.assertEqual(response.status_code, 403)

    def test_not_authorized(self):
        user = StaffFactory(course_key=self.course.id)
        access_token = AccessTokenFactory.create(user=user, client=self.oauth_client).token
        auth_header = 'Bearer ' + access_token

        # If debug mode is enabled, the view should always return data.
        with override_settings(DEBUG=True):
            response = self.http_get(reverse(self.view, kwargs={'course_id': self.course_id}),
                                     HTTP_AUTHORIZATION=auth_header)
            self.assertEqual(response.status_code, 200)

        response = self.http_get(reverse(self.view, kwargs={'course_id': self.course_id}),
                                 HTTP_AUTHORIZATION=auth_header)
        self.assertEqual(response.status_code, 200)

        # Access should be denied if the user is not course staff
        response = self.http_get(reverse(self.view, kwargs={'course_id': unicode(self.empty_course.id)}),
                                 HTTP_AUTHORIZATION=auth_header)
        self.assertEqual(response.status_code, 403)


@override_settings(MODULESTORE=TEST_DATA_MOCK_MODULESTORE)
class CourseListTests(CourseViewTestsMixin, ModuleStoreTestCase):
    view = 'course_structure_api_v0:list'

    def test_get(self):
        """
        The view should return a list of all courses.
        """
        response = self.http_get(reverse(self.view))
        self.assertEqual(response.status_code, 200)
        data = response.data
        courses = data['results']

        self.assertEqual(len(courses), 2)
        self.assertEqual(data['count'], 2)
        self.assertEqual(data['num_pages'], 1)

        self.assertValidResponseCourse(courses[0], self.empty_course)
        self.assertValidResponseCourse(courses[1], self.course)

    def test_get_with_pagination(self):
        """
        The view should return a paginated list of courses.
        """
        url = "{}?page_size=1".format(reverse(self.view))
        response = self.http_get(url)
        self.assertEqual(response.status_code, 200)

        courses = response.data['results']
        self.assertEqual(len(courses), 1)
        self.assertValidResponseCourse(courses[0], self.empty_course)

    def test_get_filtering(self):
        """
        The view should return a list of details for the specified courses.
        """
        url = "{}?course_id={}".format(reverse(self.view), self.course_id)
        response = self.http_get(url)
        self.assertEqual(response.status_code, 200)

        courses = response.data['results']
        self.assertEqual(len(courses), 1)
        self.assertValidResponseCourse(courses[0], self.course)

    def test_not_authenticated(self):
        # If debug mode is enabled, the view should always return data.
        with override_settings(DEBUG=True):
            response = self.http_get(reverse(self.view), HTTP_AUTHORIZATION=None)
            self.assertEqual(response.status_code, 200)

        response = self.http_get(reverse(self.view), HTTP_AUTHORIZATION=None)
        self.assertEqual(response.status_code, 403)

    def test_not_authorized(self):
        user = StaffFactory(course_key=self.course.id)
        access_token = AccessTokenFactory.create(user=user, client=self.oauth_client).token
        auth_header = 'Bearer ' + access_token

        # If debug mode is enabled, the view should always return data.
        with override_settings(DEBUG=True):
            response = self.http_get(reverse(self.view), HTTP_AUTHORIZATION=auth_header)
            self.assertEqual(response.status_code, 200)

        response = self.http_get(reverse(self.view), HTTP_AUTHORIZATION=auth_header)
        self.assertEqual(response.status_code, 200)

        url = "{}?course_id={}".format(reverse(self.view), self.course_id)
        response = self.http_get(url, HTTP_AUTHORIZATION=auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.data['results']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], self.course.display_name)

        # Access should be denied if the user is not course staff.
        url = "{}?course_id={}".format(reverse(self.view), unicode(self.empty_course.id))
        response = self.http_get(url, HTTP_AUTHORIZATION=auth_header)
        self.assertEqual(response.status_code, 403)


@override_settings(MODULESTORE=TEST_DATA_MOCK_MODULESTORE)
class CourseDetailTests(CourseDetailMixin, CourseViewTestsMixin, ModuleStoreTestCase):
    view = 'course_structure_api_v0:detail'

    def test_get(self):
        response = super(CourseDetailTests, self).test_get()
        self.assertValidResponseCourse(response.data, self.course)


@override_settings(MODULESTORE=TEST_DATA_MOCK_MODULESTORE)
class CourseStructureTests(CourseDetailMixin, CourseViewTestsMixin, ModuleStoreTestCase):
    view = 'course_structure_api_v0:structure'

    def test_get(self):
        """
        The view should return the structure for a course.
        """
        response = super(CourseStructureTests, self).test_get()
        blocks = {}

        def add_block(xblock):
            children = xblock.get_children()
            blocks[unicode(xblock.location)] = {
                u'usage_key': unicode(xblock.location),
                u'block_type': xblock.category,
                u'display_name': xblock.display_name,
                u'format': xblock.format,
                u'graded': xblock.graded,
                u'children': [unicode(child.location) for child in children]
            }

            for child in children:
                add_block(child)

        course = self.store.get_course(self.course.id, depth=None)

        # Include the orphaned about block
        about_block = self.store.get_item(BlockUsageLocator(self.course.id, 'about', 'overview'))

        add_block(course)
        add_block(about_block)

        expected = {
            u'root': unicode(self.course.location),
            u'blocks': blocks
        }

        self.maxDiff = None
        self.assertDictEqual(response.data, expected)


@override_settings(MODULESTORE=TEST_DATA_MOCK_MODULESTORE)
class CourseGradingPolicyTests(CourseDetailMixin, CourseViewTestsMixin, ModuleStoreTestCase):
    view = 'course_structure_api_v0:grading_policy'

    def test_get(self):
        """
        The view should return grading policy for a course.
        """
        response = super(CourseGradingPolicyTests, self).test_get()

        expected = [
            {
                "count": 24,
                "weight": 0.2,
                "assignment_type": "Homework",
                "dropped": 0
            },
            {
                "count": 4,
                "weight": 0.8,
                "assignment_type": "Exam",
                "dropped": 0
            }
        ]
        self.assertListEqual(response.data, expected)
