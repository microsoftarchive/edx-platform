"""
Tests for EmbargoMiddleware
"""

import mock
import pygeoip
import unittest

from django.core.urlresolvers import reverse
from django.conf import settings
from django.test.utils import override_settings
import ddt

from student.tests.factories import UserFactory
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import (
    ModuleStoreTestCase, mixed_store_config
)

# Explicitly import the cache from ConfigurationModel so we can reset it after each test
from config_models.models import cache
from embargo.models import EmbargoedCourse, EmbargoedState, IPFilter, RestrictedCourse, Country, CountryAccessRule, \
    WHITE_LIST, BLACK_LIST
from django_countries import countries

from util.testing import UrlResetMixin
from embargo import api as embargo_api
from embargo.exceptions import InvalidAccessPoint
from mock import patch


# Since we don't need any XML course fixtures, use a modulestore configuration
# that disables the XML modulestore.
MODULESTORE_CONFIG = mixed_store_config(settings.COMMON_TEST_DATA_ROOT, {}, include_xml=False)


@ddt.ddt
@override_settings(MODULESTORE=MODULESTORE_CONFIG)
@unittest.skipUnless(settings.ROOT_URLCONF == 'lms.urls', 'Test only valid in lms')
class EmbargoApiTests(ModuleStoreTestCase):
    """
    Tests of EmbargoApi
    """

    def setUp(self):
        self.user = UserFactory(username='fred', password='secret')
        self.client.login(username='fred', password='secret')
        self.embargo_course1 = CourseFactory.create()
        self.embargo_course1.save()
        self.embargo_course2 = CourseFactory.create()
        self.embargo_course2.save()
        self.regular_course = CourseFactory.create(org="Regular")
        self.regular_course.save()
        self.embargoed_course_whitelisted = '/courses/' + self.embargo_course1.id.to_deprecated_string() + '/info'
        self.embargoed_course_blacklisted = '/courses/' + self.embargo_course2.id.to_deprecated_string() + '/info'
        self.regular_page = '/courses/' + self.regular_course.id.to_deprecated_string() + '/info'

        restricted_course_1 = RestrictedCourse(course_key=self.embargo_course1.id)
        restricted_course_1.save()

        restricted_course_2 = RestrictedCourse(course_key=self.embargo_course2.id)
        restricted_course_2.save()

        all_countries = [Country(country=code[0]) for code in list(countries)]
        Country.objects.bulk_create(all_countries)

        country_access_white_rules = [
            CountryAccessRule(
                restricted_course=restricted_course_1,
                rule_type=WHITE_LIST,
                country=Country.objects.get(country='US')
            ),
            CountryAccessRule(
                restricted_course=restricted_course_1,
                rule_type=WHITE_LIST,
                country=Country.objects.get(country='NZ')
            )
        ]
        CountryAccessRule.objects.bulk_create(country_access_white_rules)

        country_access_black_rules = [
            CountryAccessRule(
                restricted_course=restricted_course_2,
                rule_type=BLACK_LIST,
                country=Country.objects.get(country='IR')
            ),
            CountryAccessRule(
                restricted_course=restricted_course_2,
                rule_type=BLACK_LIST,
                country=Country.objects.get(country='AF')
            )
        ]
        CountryAccessRule.objects.bulk_create(country_access_black_rules)

        # Text from lms/templates/static_templates/embargo.html
        self.embargo_text = "Unfortunately, at this time edX must comply with export controls, and we cannot allow you to access this course."

        self.patcher = mock.patch.object(pygeoip.GeoIP, 'country_code_by_addr', self.mock_country_code_by_addr)
        self.patcher.start()

    def tearDown(self):
        # Explicitly clear ConfigurationModel's cache so tests have a clear cache
        # and don't interfere with each other
        cache.clear()
        self.patcher.stop()

    def mock_country_code_by_addr(self, ip_addr):
        """
        Gives us a fake set of IPs
        """
        ip_dict = {
            '1.0.0.0': 'CU',
            '2.0.0.0': 'IR',
            '3.0.0.0': 'SY',
            '4.0.0.0': 'SD',
            '5.0.0.0': 'AQ',  # Antartica
            '2001:250::': 'CN',
            '2001:1340::': 'CU',
        }
        return ip_dict.get(ip_addr, 'US')

    @mock.patch.dict(settings.FEATURES, {'ENABLE_COUNTRY_ACCESS': True})
    @ddt.data("", "US", "CA", "AF", "NZ", "IR")
    def test_embargo_course_whitelisted_with_profile_country(self, profile_country):
        # Set the country in the user's profile
        profile = self.user.profile
        profile.country = profile_country
        profile.save()

        response = self.client.get(self.embargoed_course_whitelisted)
        # Course is whitelisted against US,NZ so all other countries will be disallowed
        if profile_country in ["CA", "AF", "IR"]:
            embargo_url = reverse('embargo')
            self.assertRedirects(response, embargo_url)
        else:
            self.assertEqual(response.status_code, 200)


    @mock.patch.dict(settings.FEATURES, {'ENABLE_COUNTRY_ACCESS': True})
    @ddt.data("", "US", "CA", "NZ", "IR", "AF")
    def test_embargo_course_blacklisted_with_profile_country(self, profile_country):
        # Set the country in the user's profile
        profile = self.user.profile
        profile.country = profile_country
        profile.save()

        response = self.client.get(self.embargoed_course_blacklisted)
        if profile_country in ["", "US", "CA", "NZ"]:
            self.assertEqual(response.status_code, 200)
        else:
            embargo_url = reverse('embargo')
            self.assertRedirects(response, embargo_url)






# TODO -- remove this whitespace; it's only here to avoid
# merge conflicts with Awais's branch.
@ddt.ddt
@override_settings(MODULESTORE=MODULESTORE_CONFIG)
@unittest.skipUnless(settings.ROOT_URLCONF == 'lms.urls', 'Test only valid in lms')
class EmbargoMessageUrlApiTests(UrlResetMixin, ModuleStoreTestCase):
    """Test the embargo API calls for retrieving the blocking message URLs. """

    @patch.dict(settings.FEATURES, {'ENABLE_COUNTRY_ACCESS': True})
    def setUp(self):
        super(EmbargoMessageUrlApiTests, self).setUp('embargo')
        self.course = CourseFactory.create()

    @ddt.data(
        ('enrollment', '/embargo/blocked-message/enrollment/embargo/'),
        ('courseware', '/embargo/blocked-message/courseware/embargo/')
    )
    @ddt.unpack
    def test_message_url_path(self, access_point, expected_url_path):
        self._restrict_course(self.course.id)

        # Retrieve the URL to the blocked message page
        url_path = embargo_api.message_url_path(self.course.id, access_point)
        self.assertEqual(url_path, expected_url_path)

    def test_message_url_path_caching(self):
        self._restrict_course(self.course.id)

        # The first time we retrieve the message, we'll need
        # to hit the database.
        with self.assertNumQueries(2):
            embargo_api.message_url_path(self.course.id, "enrollment")

        # The second time, we should be using cached values
        with self.assertNumQueries(0):
            embargo_api.message_url_path(self.course.id, "enrollment")

    @ddt.data('enrollment', 'courseware')
    def test_message_url_path_no_restrictions_for_course(self, access_point):
        # No restrictions for the course
        url_path = embargo_api.message_url_path(self.course.id, access_point)

        # Use a default path
        self.assertEqual(url_path, '/embargo/blocked-message/courseware/default/')

    def test_invalid_access_point(self):
        with self.assertRaises(InvalidAccessPoint):
            embargo_api.message_url_path(self.course.id, "invalid")

    def _restrict_course(self, course_key):
        """Restrict the user from accessing the course. """
        country = Country.objects.create(country='us')
        restricted_course = RestrictedCourse.objects.create(
            course_key=course_key,
            enroll_msg_key='embargo',
            access_msg_key='embargo'
        )
        CountryAccessRule.objects.create(
            restricted_course=restricted_course,
            rule_type=BLACK_LIST,
            country=country
        )
