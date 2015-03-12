import hashlib

from django.conf import settings
from django.test import TestCase

from openedx.core.djangoapps.user_api.accounts.helpers import get_profile_image_url_for_user
from student.tests.factories import UserFactory

PROFILE_IMAGE_URL_PATH = settings.PROFILE_IMAGE_BASE_URL + settings.PROFILE_IMAGE_URL_PATH


class ProfileImageUrlTestCase(TestCase):
    """
    Tests for `get_profile_image_url_for_user`.
    """
    def setUp(self):
        self.user = UserFactory()

    def test_has_no_profile_image(self):
        """
        Verify we get the URL to the default image if the user does not
        have a profile image.
        """
        self.assertEqual(
            get_profile_image_url_for_user(self.user),
            PROFILE_IMAGE_URL_PATH + settings.PROFILE_IMAGE_DEFAULT_FILENAME
        )

    def test_has_profile_image(self):
        """
        Verify we get the correct URL to the user's image when the user
        has a profile image.  The convention is:
            <storage-backend-domain>/<path-to-file>/<salted-md5-hash-of-username>.jpg
        """
        self.user.profile.has_profile_image = True
        self.assertEqual(
            get_profile_image_url_for_user(self.user),
            '{}.jpg'.format(PROFILE_IMAGE_URL_PATH + hashlib.md5(settings.PROFILE_IMAGE_SECRET_KEY + self.user.username).hexdigest())
        )
