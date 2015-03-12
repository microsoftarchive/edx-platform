"""
Helper functions for the accounts API.
"""
import hashlib

from django.conf import settings
from django.core.files.storage import FileSystemStorage, get_storage_class


def get_profile_image_url_for_user(user):
    """Given a user, return the URL to that user's profile image.

    If the user has not yet uploaded a profile image, return the URL to
    the default edX user profile image.

    Arguments:
        user (django.auth.User): The user for whom we're generating a
        profile image URL.

    Returns:
        string: The URL for the user's profile image.
    """
    if user.profile.has_profile_image:
        filename = '{}.jpg'.format(hashlib.md5(settings.PROFILE_IMAGE_SECRET_KEY + user.username).hexdigest())
    else:
        filename = settings.PROFILE_IMAGE_DEFAULT_FILENAME

    # Note that, for now, the backend will be FileSystemStorage.  When
    # we eventually support s3 storage, we'll need to pass a parameter
    # to the storage class indicating the s3 bucket which we're using
    # for profile picture uploads.
    storage_class = get_storage_class(settings.PROFILE_IMAGE_BACKEND)
    if storage_class == FileSystemStorage:
        kwargs = {'base_url': settings.PROFILE_IMAGE_BASE_URL + settings.PROFILE_IMAGE_URL_PATH}
    storage = storage_class(**kwargs)
    return storage.url(filename)
