from ddt import ddt, data
import hashlib
from mock import patch

from django.test import TestCase

from openedx.core.djangoapps.user_api.accounts.helpers import get_profile_image_url_for_user
from student.tests.factories import UserFactory

from .utils import ProfileImageUrlTestCaseMixin


@ddt
@patch.dict(
    'openedx.core.djangoapps.user_api.accounts.helpers.PROFILE_IMAGE_SIZES', {'full': 50}, clear=True
)
class ProfileImageUrlTestCase(ProfileImageUrlTestCaseMixin, TestCase):
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
        self.user.has_profile_image = False
        self.assertEqual(
            get_profile_image_url_for_user(self.user, 50),
            'http://example-storage.com/profile_images/default_50.jpg'
        )

    def test_has_profile_image(self):
        """
        Verify we get the correct URL to the user's image when the user
        has a profile image.  The convention is:
            <storage-backend-domain>/<path-to-file>/<salted-md5-hash-of-username>_<image_size>.jpg
        """
        self.user.profile.has_profile_image = True
        expected_filename = '{}_50.jpg'.format(hashlib.md5('secret' + self.user.username).hexdigest())
        self.assertEqual(
            get_profile_image_url_for_user(self.user, 50),
            'http://example-storage.com/profile_images/{}'.format(expected_filename)
        )

    @data(1, 5000)
    def test_unsupported_sizes(self, image_size):
        """
        Verify that we cannot ask for image sizes which are unsupported.
        """
        with self.assertRaises(ValueError):
            get_profile_image_url_for_user(self.user, image_size)
