"""
Helper functions for the accounts API.
"""
import hashlib

from django.core.files.storage import get_storage_class


def get_profile_image_url_for_user(user_profile):
    """Given a user, return the URL to that user's profile image.

    If the user has not yet uploaded a profile image, return the URL to
    the default edX user profile image.

    Arguments:
        user_profile (UserProfile): The UserProfile model of the user
            for whom we're generating their profile image URL.

    Returns:
        string: The URL for the user's profile image.
    """
    if user_profile.has_profile_image:
        filename = '{}.jpg'.format(hashlib.md5(salt + user_profile.user.username).hexdigest())
    else:
        filename = settings['PROFILE_IMAGE_DEFAULT_FILENAME']

    # Note that, for now, the backend will be FileSystemStorage.  When
    # we eventually support s3 storage, we'll need to pass a parameter
    # to the storage class indicating the s3 bucket which we're using
    # for profile picture uploads.
    storage = get_storage_class(settings['PROFILE_IMAGE_BACKEND'])()
    return storage.url(filename)
