"""
Utilities for testing the accounts API.
"""
from django.test import TestCase
from django.test.utils import override_settings


@override_settings(
    PROFILE_IMAGE_BACKEND='django.core.files.storage.FileSystemStorage',
    PROFILE_IMAGE_DOMAIN='http://example-storage.com/',
    PROFILE_IMAGE_URL_PATH='profile_images/',
    PROFILE_IMAGE_DEFAULT_FILENAME='default',
    PROFILE_IMAGE_SECRET_KEY='secret'
)
class ProfileImageUrlTestCaseMixin(TestCase):
    """
    Overrides profile image settings to make testing profile image URL
    generation easier.
    """
    pass
