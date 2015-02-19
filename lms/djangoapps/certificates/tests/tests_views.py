"""
Django Unit Tests for Certificates web views
"""
from uuid import uuid4

from django.conf import settings
from django.test.client import Client
from django.test.utils import override_settings

from certificates.models import GeneratedCertificate
from student.tests.factories import UserFactory
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

FEATURES_WITH_CERTS_ENABLED = settings.FEATURES.copy()
FEATURES_WITH_CERTS_ENABLED['CERTIFICATES_HTML_VIEW'] = True

FEATURES_WITH_CERTS_DISABLED = settings.FEATURES.copy()
FEATURES_WITH_CERTS_DISABLED['CERTIFICATES_HTML_VIEW'] = False


class CertificatesViewsTests(ModuleStoreTestCase):
    """
    Tests for the manual refund page
    """
    def setUp(self):
        super(CertificatesViewsTests, self).setUp()
        self.client = Client()
        self.course = CourseFactory.create(
            org='testorg', number='run1', display_name='refundable course'
        )
        self.course_id = self.course.location.course_key
        self.user = UserFactory.create(
            email='joe_user@edx.org',
            username='joeuser',
            password='foo'
        )
        self.user.profile.name = "Joe User"
        self.user.profile.save()
        self.client.login(username=self.user.username, password='foo')

        self.cert = GeneratedCertificate.objects.create(
            user=self.user,
            course_id=self.course_id,
            verify_uuid=uuid4(),
            download_uuid=uuid4(),
            grade="0.95",
            key='the_key',
            distinction=True,
            status='generated',
            mode='honor',
            name=self.user.profile.name,
        )

    @override_settings(FEATURES=FEATURES_WITH_CERTS_ENABLED)
    def test_render_html_view_valid_certificate(self):
        test_url = '/certificates/html?course={}'.format(unicode(self.course.id))
        response = self.client.get(test_url)
        self.assertIn(str(self.cert.verify_uuid), response.content)

    @override_settings(FEATURES=FEATURES_WITH_CERTS_DISABLED)
    def test_render_html_view_invalid_feature_flag(self):
        test_url = '/certificates/html?course={}'.format(unicode(self.course.id))
        response = self.client.get(test_url)
        self.assertIn('invalid', response.content)

    @override_settings(FEATURES=FEATURES_WITH_CERTS_ENABLED)
    def test_render_html_view_missing_course_id(self):
        test_url = '/certificates/html'
        response = self.client.get(test_url)
        self.assertIn('invalid', response.content)

    @override_settings(FEATURES=FEATURES_WITH_CERTS_ENABLED)
    def test_render_html_view_invalid_course_id(self):
        test_url = '/certificates/html?course=az-23423-4vs'
        response = self.client.get(test_url)
        self.assertIn('invalid', response.content)

    @override_settings(FEATURES=FEATURES_WITH_CERTS_ENABLED)
    def test_render_html_view_invalid_course(self):
        test_url = '/certificates/html?course=missing/course/key'
        response = self.client.get(test_url)
        self.assertIn('invalid', response.content)

    @override_settings(FEATURES=FEATURES_WITH_CERTS_ENABLED)
    def test_render_html_view_invalid_certificate(self):
        self.cert.delete()
        self.assertEqual(len(GeneratedCertificate.objects.all()), 0)
        test_url = '/certificates/html?course={}'.format(unicode(self.course.id))
        response = self.client.get(test_url)
        self.assertIn('invalid', response.content)
